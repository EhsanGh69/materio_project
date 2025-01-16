from django.forms import ModelForm

from blog.models import Category


class AddCategoryForm(ModelForm):
    use_required_attribute = False
    class Meta:
        model = Category
        fields = "__all__"

