from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import View
from .models import Company
from .forms import CompanyProfileForm
from JobBoardPortal.accounts.mixins import EmployerRequiredMixin


@method_decorator(login_required, name='dispatch')
class CompanyProfileView(EmployerRequiredMixin, View):
    """View for managing company profile"""
    
    def get(self, request):
        """Display company profile form"""
        # Double-check user type (should be handled by mixin, but extra safety)
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'employer':
            messages.error(request, 'Access denied. Only employers can manage company profiles.')
            return redirect('accounts:profile')
        
        try:
            company = Company.objects.get(user=request.user)
            form = CompanyProfileForm(instance=company)
            context = {
                'form': form,
                'company': company,
                'is_edit': True
            }
        except Company.DoesNotExist:
            form = CompanyProfileForm()
            context = {
                'form': form,
                'company': None,
                'is_edit': False
            }
        
        return render(request, 'companies/profile.html', context)
    
    def post(self, request):
        """Handle company profile form submission"""
        # Double-check user type (should be handled by mixin, but extra safety)
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'employer':
            messages.error(request, 'Access denied. Only employers can manage company profiles.')
            return redirect('accounts:profile')
        
        try:
            company = Company.objects.get(user=request.user)
            form = CompanyProfileForm(request.POST, request.FILES, instance=company)
            is_edit = True
        except Company.DoesNotExist:
            form = CompanyProfileForm(request.POST, request.FILES)
            is_edit = False
        
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()
            
            if is_edit:
                messages.success(request, 'Company profile updated successfully!')
            else:
                messages.success(request, 'Company profile created successfully!')
            
            return redirect('companies:profile')
        
        context = {
            'form': form,
            'company': company if is_edit else None,
            'is_edit': is_edit
        }
        return render(request, 'companies/profile.html', context)


@login_required
def company_detail(request, company_id):
    """View for displaying company details (public view)"""
    company = get_object_or_404(Company, id=company_id)
    context = {
        'company': company
    }
    return render(request, 'companies/detail.html', context)