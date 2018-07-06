from django import forms
# from captcha.fields import CaptchaField

# 登陆表单
class LoginForm(forms.Form):
    cus_id = forms.CharField(label='学号/教工号', max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cus_password = forms.CharField(label='密码', max_length=128,
                                   widget=forms.PasswordInput(attrs={'class': 'form-control'}))


# 注册表单
class RegisterForm(forms.Form):
    gender = (('male', '男'), ('female', '女'),)
    # 学生学号，教师教工号，管理员无此选项
    cus_id = forms.CharField(label="学号/教工号", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # 真实姓名，可以重复
    cus_name = forms.CharField(label="姓名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # 专业
    cus_major = forms.CharField(max_length=128, label="专业", widget=forms.TextInput(attrs={'class': 'form-control'}))
    # 学院
    cus_college = forms.CharField(max_length=128, label="学院", widget=forms.TextInput(attrs={'class': 'form-control'}))
    # 密码
    cus_password_1 = forms.CharField(label="密码", max_length=256,
                                     widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    cus_password_2 = forms.CharField(label="确认密码", max_length=256,
                                     widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # 邮箱
    cus_email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    # 性别
    cus_sex = forms.ChoiceField(label='性别', choices=gender)


class AttachFileForm(forms.Form):
    file = forms.FileField(label="文件")


# 项目关联的文件
class ProjectFileForm(forms.Form):
    pro_fil_text = forms.CharField(label='提交文件', max_length=500, )
    pro_file = forms.FileField(label="文件")


# 公共文件
class AllFileForm(forms.Form):
    all_fil_text = forms.CharField(label='文件描述', max_length=128,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    all_file = forms.FileField(label="文件", widget=forms.FileInput(attrs={}))
