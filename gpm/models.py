from django.db import models


# 课题
class Project(models.Model):
    # 课题发布人
    pro_from_user = models.CharField(max_length=500, null=True)
    pro_from_user_id = models.CharField(max_length=500, null=True)
    pro_text = models.TextField(null=True)
    pro_title = models.CharField(max_length=50, null=True)
    pro_pub_date = models.DateTimeField('课题发布日期', auto_now_add=True)


# 公告
class Announcement(models.Model):
    ann_text = models.TextField(null=True)
    ann_title = models.CharField(max_length=50, null=True)
    ann_pub_date = models.DateTimeField('公告发布日期', auto_now_add=True)


# 规定
class Regulation(models.Model):
    reg_text = models.TextField(null=True)
    reg_title = models.CharField(max_length=50, null=True)
    reg_pub_date = models.DateTimeField('规定发布日期', auto_now_add=True)


# 新闻
class Journalism(models.Model):
    jou_text = models.TextField(null=True)
    jou_title = models.CharField(max_length=50, null=True)
    jou_pub_date = models.DateTimeField('新闻发布日期', auto_now_add=True)


class Customer(models.Model):
    # 性别
    gender = (
        ('male', '男'),
        ('female', '女'),
    )

    # 管理员不提供注册功能，老师需要人工审核
    # 默认注册为学生
    role = (
        ('student', '学生'),
        ('teacher', '老师'),
        ('administrator', '管理员'),
    )
    # 学生学号，教师教工号，管理员无此选项
    cus_id = models.CharField(max_length=128, unique=True)
    # 真实姓名，可以重复
    cus_name = models.CharField(max_length=128, default='未实名认证')
    # 专业
    cus_major = models.CharField(max_length=128, default='未选择专业')
    # 学院
    cus_college = models.CharField(max_length=128, default='未选择学院')
    # 密码
    cus_password = models.CharField(max_length=256)
    # 邮箱
    cus_email = models.EmailField(unique=True)
    # 性别
    cus_sex = models.CharField(max_length=32, choices=gender, default='男')
    # 注册时间
    cus_join_time = models.DateTimeField(auto_now_add=True)
    # 是否确认注册
    # 用户类别
    cus_role = models.CharField(max_length=20, choices=role, default='学生')
    # 用户所选课题id（针对学生）

    cus_urge = models.BooleanField(default=False)
    cus_project_file = models.BooleanField(default=False)
    cus_project_id = models.IntegerField(null=True, default=None)


class Question(models.Model):
    que_text = models.CharField(max_length=512, null=True)
    que_read = models.BooleanField(default=False)

    # 提问者，被提问者，这里使用教工号 或者 学号
    que_from_user = models.CharField(max_length=500, null=True)
    que_to_user = models.CharField(max_length=500, null=True)
    que_send_date = models.DateTimeField('ask question', auto_now_add=True, null=True)
    # 是否已经回复
    que_replay = models.BooleanField(default=False)


class Answer(models.Model):
    ans_text = models.CharField(max_length=512, null=True)
    ans_read = models.BooleanField(default=False)

    # 提问者，被提问者，这里使用教工号 或者 学号
    ans_from_user = models.CharField(max_length=500, null=True)
    ans_to_user = models.CharField(max_length=500, null=True)
    ans_send_date = models.DateTimeField('answer question', auto_now_add=True, null=True)
    # 关联的相应的问题
    ans_que_id = models.IntegerField(null=True)


class Evaluate(models.Model):
    eva_text = models.CharField(max_length=512, null=True)
    # 评价者与被评价者这里使用教工号 或者 学号
    eva_from_user = models.CharField(max_length=500, null=True)
    eva_to_user = models.CharField(max_length=500, null=True)
    eva_send_date = models.DateTimeField('answer question', auto_now_add=True, null=True)


# 项目关联的文件
class ProjectFile(models.Model):
    # 文件接受者
    pro_fil_upload_to_user = models.CharField(max_length=500, null=True)
    # 项目文件 文件名
    pro_fil_name = models.CharField(max_length=30)
    # 项目文件 上传者
    pro_fil_upload_from_user = models.CharField(max_length=500, null=True)
    # 文件关联的项目
    pro_fil_pro_id = models.IntegerField(null=True)
    # 文件的描述
    pro_fil_text = models.TextField(null=True)
    # 文件上传时间
    pro_fil_pub_date = models.DateTimeField('文件上传日期', auto_now_add=True)
    # 文件
    pro_file = models.FileField('文件', upload_to='./uploads/projects', null=True)


# 公共文件
class AllFile(models.Model):
    # 项目文件 文件名
    all_fil_name = models.CharField(max_length=30)
    # 项目文件 上传者
    all_fil_upload_from_user = models.CharField(max_length=500, null=True)
    # 文件的描述
    all_fil_text = models.TextField(null=True)
    # 文件上传时间
    all_fil_pub_date = models.DateTimeField('文件上传日期', auto_now_add=True)
    # 公共文件
    all_file = models.FileField('文件', upload_to='./uploads/all', null=True)
