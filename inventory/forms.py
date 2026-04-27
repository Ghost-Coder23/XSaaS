from django import forms
from .models import AssetCategory, AssetItem

class AssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = ['name', 'description']

class AssetItemForm(forms.ModelForm):
    class Meta:
        model = AssetItem
        fields = ['category', 'name', 'description', 'quantity', 'condition', 'location']
