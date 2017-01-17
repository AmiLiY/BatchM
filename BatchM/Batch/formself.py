from django.forms import Form,ModelForm
# ModelForm把 models里到数据变成一个表单，可以用的html页面上
from  Batch import models


class ApplyUpdateForm(ModelForm):
    class Meta:
        model = models.WorkOrderOfUpdate
        exclude = ('email_issend','tags',)


    def __init__(self, *args, **kwargs):
        #  继承父类，后重写自己的类
        super(ApplyUpdateForm, self).__init__(*args, **kwargs)

        for field_name in self.base_fields:
            field = self.base_fields[field_name]
            field.widget.attrs.update({'class': 'form-control'})



class Docker_Containers(ModelForm):
    class Meta:
        model = models.DockerContainers
        exclude = ()

    def __init__(self, *args, **kwargs):
        #  继承父类，后重写自己的类
        super(Docker_Containers, self).__init__(*args, **kwargs)
        for field_name in self.base_fields:
            field = self.base_fields[field_name]
            field.widget.attrs.update({'class': 'form-control'})