from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import CustomUserChangeForm


# Create your views here.
def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/workspaces/')
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/update.html', context)


def delete(request):
    if request.user.is_authenticated:
        request.user.delete()
        logout(request)
    return redirect('/accounts/login/')