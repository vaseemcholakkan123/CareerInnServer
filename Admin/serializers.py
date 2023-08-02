from rest_framework import serializers
from .models import News
from Employer.models import Department,Company

class NewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = '__all__'

class AdminDepartmentSerializer(serializers.ModelSerializer):

    no_of_company = serializers.SerializerMethodField()

    class Meta:
        model = Department     
        fields = ('title','no_of_company' , 'id')

    def get_no_of_company(self,obj):
        return Company.objects.filter(department=obj).count()