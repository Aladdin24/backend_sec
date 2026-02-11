from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category
from .forms import CategoryForm
from .permissions import IsAdminUser

# Décorateur personnalisé pour les vues classiques
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not IsAdminUser().has_permission(request, view_func):
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_categories_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'admin_dashboard/categories_list.html', {'categories': categories})

@admin_required
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            if Category.objects.filter(name__iexact=name).exists():
                messages.error(request, "Cette catégorie existe déjà.")
            else:
                form.save()
                messages.success(request, "Catégorie créée avec succès.")
                return redirect('admin_categories_list')
    else:
        form = CategoryForm()
    return render(request, 'admin_dashboard/category_form.html', {
        'form': form,
        'title': 'Créer une catégorie'
    })

@admin_required
def admin_category_update(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            name = form.cleaned_data['name']
            # Vérifier unicité (sauf pour le nom actuel)
            if Category.objects.filter(name__iexact=name).exclude(id=category_id).exists():
                messages.error(request, "Ce nom de catégorie est déjà utilisé.")
            else:
                form.save()
                messages.success(request, "Catégorie mise à jour.")
                return redirect('admin_categories_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_dashboard/category_form.html', {
        'form': form,
        'title': 'Modifier la catégorie',
        'category': category
    })

@admin_required
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    # Empêcher la suppression si des documents y sont liés
    if category.document_set.exists():
        messages.error(request, "Impossible de supprimer une catégorie contenant des documents.")
        return redirect('admin_categories_list')
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Catégorie supprimée.")
        return redirect('admin_categories_list')
    
    return render(request, 'admin_dashboard/category_confirm_delete.html', {'category': category})