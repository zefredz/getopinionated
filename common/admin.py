from django.contrib import admin

### define actions ###
def delete_action(modeladmin, request, queryset):
    for item in queryset:
        item.override_mutability(True)
        item.delete()
delete_action.short_description = "Delete selection."

def disable_action(modeladmin, request, queryset):
    queryset.update(enabled=False)
disable_action.short_description = "Disable selection (preferred instead of delete)."

### define ModelAdmins ###
class OverrideImmutabilityAdmin(admin.ModelAdmin):
    save_as = True
    show_save = False
    actions = [delete_action]

    def has_change_permission(self, request, obj=None):
        """ [overridden] Override mutability if user has permission (needs to happen at an early stage to avoid errors) """
        has_permission = super(OverrideImmutabilityAdmin, self).has_change_permission(request, obj)
        if obj and has_permission:
            obj.override_mutability(True)
        return has_permission

    def delete_model(self, request, obj):
        """ [overridden] Override mutability before deleting the object """
        obj.override_mutability(True)
        super(OverrideImmutabilityAdmin, self).delete_model(request, obj)

    def get_actions(self, request):
        """ [overridden] Remove the delete action because it doesn't work on multiple objects, instead
        use our custom delete_action.

        """
        actions = super(OverrideImmutabilityAdmin, self).get_actions(request)
        actions.pop('delete_selected', None) # remove delete_selected action if it exists
        return actions

class DisableableModelAdmin(OverrideImmutabilityAdmin):
    actions = OverrideImmutabilityAdmin.actions + [disable_action]
