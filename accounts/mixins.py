# accounts/mixins.py
from django.contrib.auth.mixins import AccessMixin

class GroupRequiredMixin(AccessMixin):
    group_required = None  # 'Medico' or ['Director','Admin']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        allowed = False
        groups = self.group_required if isinstance(self.group_required, (list,tuple)) else [self.group_required]
        for g in groups:
            if request.user.groups.filter(name=g).exists():
                allowed = True
                break
        if not allowed:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
