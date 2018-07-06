import hashlib

from django.http import FileResponse
from django.shortcuts import redirect
from django.shortcuts import render

from . import form
from . import models


# 通知跳转函数
def notify_and_jump(request, url, message):
    return render(request, 'gpm/notify_and_jump.html', locals())


# 测试函数
def just_test(request):
    return render(request, "gpm/file.html")


# 用户信息
def userinfo(request):
    if not request.session.get('is_login', None):
        message = '请登录后操作，谢谢，O(∩_∩)O'
        return render(request, 'gpm/notify_and_jump.html', locals())
    else:
        # 返回用户信息
        cus_id_str = request.session.get('cus_id_str')
        cus_info = models.Customer.objects.get(cus_id=cus_id_str)
        cus_project = None
        if request.session.get('cus_role') == 'student':
            student = models.Customer.objects.get(cus_id=cus_id_str)
            cus_project_id = student.cus_project_id
            if cus_project_id:
                cus_project = models.Project.objects.get(id=int(cus_project_id))
        return render(request, 'gpm/userinfo.html', locals())


# 学生管理
def student(request):
    # 未登录
    if not request.session.get('is_login', None):
        message = '请登录后操作，谢谢，O(∩_∩)O'
        return notify_and_jump(request, '/login', message)

    cus_role = request.session.get('cus_role', None)
    cus_id_str = request.session.get('cus_id_str', None)
    if cus_role == 'student':
        return redirect('/userinfo')
    students_ret = None
    if cus_role == 'administrator':
        co = request.GET.get('co', None)
        stu_id = request.GET.get('stu_id', None)
        if co and stu_id:
            # print('co stu')
            if co == 're':
                try:
                    student_t = models.Customer.objects.get(cus_id=stu_id)
                    student_t.delete()
                    message = '删除成功'
                    return notify_and_jump(request, '/student', message)
                except:
                    message = '该用户不存在'
                    return notify_and_jump(request, '/student', message)

        students_ret = models.Customer.objects.filter(cus_role='student')
    elif cus_role == 'teacher':
        co = request.GET.get('co', None)
        stu_id = request.GET.get('stu_id', None)
        if co and stu_id:
            if co == 're':
                try:
                    student_t = models.Customer.objects.get(cus_id=stu_id)
                    student_t.delete()
                    message = '删除成功'
                    return notify_and_jump(request, '/student', message)
                except:
                    message = '该用户不存在'
                    return notify_and_jump(request, '/student', message)
            elif co == 'ur':
                try:
                    student_t = models.Customer.objects.get(cus_id=stu_id)
                    student_t.cus_urge = True
                    student_t.save()
                    message = '催交成功'
                    return notify_and_jump(request, '/student', message)
                except:
                    message = '该用户不存在'
                    return notify_and_jump(request, '/student', message)

        students_ret_ = []
        students_ret = models.Customer.objects.filter(cus_role='student')
        for stu_ in students_ret:
            if stu_.cus_project_id:
                project = models.Project.objects.get(id=int(stu_.cus_project_id))
                if project.pro_from_user_id == cus_id_str:
                    students_ret_.append(stu_)
        students_ret = students_ret_

    return render(request, 'gpm/student.html', locals())


# 首页
def index(request):
    # 更新首页数据
    projects = models.Project.objects.all().order_by('-pro_pub_date')[:10]
    announcements = models.Announcement.objects.all().order_by('-ann_pub_date')[:10]
    regulations = models.Regulation.objects.all().order_by('-reg_pub_date')[:10]
    journalism = models.Journalism.objects.all().order_by('-jou_pub_date')[:10]
    public_files = models.AllFile.objects.all().order_by('-all_fil_pub_date')[:10]
    # print(public_files)
    # 获取通知
    notice_cnt = 0
    if request.session.get('is_login'):
        try:
            to_cus_id_str = request.session.get('cus_id_str')
            cus_role = request.session.get('cus_role')
            # print(to_cus_id_str)
            # print(cus_role)
            notice_ret = []

            if cus_role == 'student':
                student_ = models.Customer.objects.get(cus_id=to_cus_id_str)
                student_ur = student_.cus_urge
                answers = models.Answer.objects.all()
                for answer in answers:
                    if answer.ans_to_user == to_cus_id_str and not answer.ans_read:
                        notice_ret.append(answer)
            elif cus_role == 'teacher':
                questions = models.Question.objects.all()
                for question in questions:
                    if question.que_to_user == to_cus_id_str and not question.que_read:
                        notice_ret.append(question)
            notice_cnt = len(notice_ret)
        except Exception:
            # print('Query Error ! ! !')
            notice_cnt = 0
    return render(request, 'gpm/index.html', locals())


# 登陆
def login(request):
    # 已经登录过，不再允许登陆
    if request.session.get('is_login', None):
        return notify_and_jump(request, '/index', '您已登陆，系统将于两秒后返回系统首页！')
    if request.method == 'POST':
        login_form = form.LoginForm(request.POST)
        message = ''
        if login_form.is_valid():
            cus_id = login_form.cleaned_data['cus_id']
            cus_password = login_form.cleaned_data['cus_password']
            try:
                customer = models.Customer.objects.get(cus_id=cus_id)
                # print(customer)
                # print(cus_id, cus_password)
                # print(customer.cus_sex)
                # print(customer.cus_role)
                if customer.cus_password == hash_code(cus_password):  # 哈希值和数据库内的值进行比对
                    request.session['is_login'] = True
                    request.session['cus_id_int'] = customer.id
                    request.session['cus_id_str'] = customer.cus_id
                    request.session['cus_name'] = customer.cus_name
                    request.session['cus_role'] = customer.cus_role
                    return notify_and_jump(request, '/index', '您已登陆成功，系统将于两秒后返回系统首页！')
                else:
                    message = '您的密码填写好像不对，请核对后再试！'
            except:
                message = '该用户目前不存在，请核对后再试！'
        else:
            message = '请检查您的输入是否正确！'
    else:
        login_form = form.LoginForm()
    return render(request, 'gpm/login.html', locals())


# 注册
def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册
        return notify_and_jump(request, '/index', '您已登陆成功，无需注册！')
    if request.method == "POST":
        register_form = form.RegisterForm(request.POST)
        message = ""
        if register_form.is_valid():  # 获取数据
            cus_id = register_form.cleaned_data['cus_id']
            cus_college = register_form.cleaned_data['cus_college']
            cus_email = register_form.cleaned_data['cus_email']
            cus_major = register_form.cleaned_data['cus_major']
            cus_name = register_form.cleaned_data['cus_name']
            cus_password_1 = register_form.cleaned_data['cus_password_1']
            cus_password_2 = register_form.cleaned_data['cus_password_2']
            cus_sex = register_form.cleaned_data['cus_sex']
            if cus_password_1 != cus_password_2:  # 判断两次密码是否相同
                message = "两次输入的密码不同，请重试！"
                return render(request, 'gpm/register.html', locals())
            else:
                has_cus_id = models.Customer.objects.filter(cus_id=cus_id)
                if has_cus_id:  # 用户名ID唯一
                    message = '该(学号/教工号)已被注册，如果有人冒充了您的ID，请联系管理员'
                    return render(request, 'gpm/register.html', locals())
                has_cus_email = models.Customer.objects.filter(cus_email=cus_email)
                if has_cus_email:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请更换邮箱后重试！'
                    return render(request, 'gpm/register.html', locals())

                # 当一切都OK的情况下，创建新用户
                cus_id = register_form.cleaned_data['cus_id']
                cus_college = register_form.cleaned_data['cus_college']
                cus_email = register_form.cleaned_data['cus_email']
                cus_major = register_form.cleaned_data['cus_major']
                cus_name = register_form.cleaned_data['cus_name']
                cus_password_1 = register_form.cleaned_data['cus_password_1']
                cus_password_2 = register_form.cleaned_data['cus_password_2']
                cus_sex = register_form.cleaned_data['cus_sex']

                new_customer = models.Customer()
                new_customer.cus_id = cus_id
                new_customer.cus_college = cus_college
                new_customer.cus_email = cus_email
                new_customer.cus_major = cus_major
                new_customer.cus_name = cus_name
                new_customer.cus_sex = cus_sex
                new_customer.cus_role = 'student'
                new_customer.cus_password = hash_code(cus_password_1)
                new_customer.save()

                return notify_and_jump(request, '/login', '您已注册成功，即将跳转到登陆界面！')
        else:
            message = '请检查输入是否正确，蟹蟹合作'
            return render(request, 'gpm/register.html', locals())
    else:
        register_form = form.RegisterForm()
        return render(request, 'gpm/register.html', locals())


# 注销
def logout(request):
    if request.session.get('is_login', None):
        request.session.flush()
    return notify_and_jump(request, '/index', '您已注销登陆！')


# 文章，项目，发布
def publish(request):
    if not request.session.get('is_login', None):
        message = '请登录后尝试此操作，谢谢！'
        return notify_and_jump(request, '/login', message)

    message = ''
    cus_id_str = request.session['cus_id_str']
    cus_name = request.session['cus_name']
    req_cus_role = request.session['cus_role']

    if request.method == 'POST':
        pos_title = request.POST.get('title')
        pos_text = request.POST.get('text')

        if pos_title.strip().replace('\n', '') and pos_text.strip().replace('\n', ''):
            # print(pos_title)
            # print(pos_text)
            pass
        else:
            # print('请不要提交空内容')
            message = '请不要提交空内容'
            return render(request, 'gpm/publish.html', locals())
        if req_cus_role == 'teacher':
            project_ = models.Project()
            project_.pro_from_user = cus_name
            project_.pro_title = pos_title
            project_.pro_text = pos_text
            project_.pro_from_user_id = cus_id_str
            project_.save()
            # print('教师项目发布完毕')
            cus_project = project_
            message = '课题发布完毕'
            return notify_and_jump(request, '/project?pid=' + str(cus_project.id), message)
        elif req_cus_role == 'administrator':
            if request.method == 'POST':
                pos_category = request.POST.get('pos_category')
                # print(pos_category)
                # print(request.POST.get('title'))
                # print(request.POST.get('text'))
                if pos_category == 'ann':
                    announcement_ = models.Announcement()
                    announcement_.ann_title = request.POST.get('title')
                    announcement_.ann_text = request.POST.get('text')
                    announcement_.save()
                    message = '公告发布完毕'
                    return notify_and_jump(request, '/passage?pos_category=ann&pid=' + str(announcement_.id),
                                           message)

                elif pos_category == 'reg':
                    regulation_ = models.Regulation()
                    regulation_.reg_title = request.POST.get('title')
                    regulation_.reg_text = request.POST.get('text')
                    regulation_.save()
                    message = '规定发布完毕'
                    return notify_and_jump(request,
                                           '/passage?pos_category=reg&pid=' + str(regulation_.id),
                                           message)
                elif pos_category == 'jou':
                    journalism_ = models.Journalism()
                    journalism_.jou_title = request.POST.get('title')
                    journalism_.jou_text = request.POST.get('text')
                    journalism_.save()
                    message = '新闻动态发布完毕'
                    return notify_and_jump(request, '/passage?pos_category=jou&pid=' + str(journalism_.id),
                                           message)
                else:
                    message = '文章分类不合法'
                    return render(request, 'gpm/publish.html', locals())
        else:
            message = '您来到了外星球，即将返回系统首页'
            return notify_and_jump(request, '/index', message)
    else:
        if req_cus_role == 'student':
            message = '您来到了外星球，即将返回系统首页'
            return notify_and_jump(request, '/index', message)
        else:
            return render(request, 'gpm/publish.html', locals())


# 文章界面
def passage(request):
    if not request.session.get('is_login', None):
        message = '请登录后操作，谢谢，O(∩_∩)O'
        return notify_and_jump(request, '/login', message)

    if request.method == 'GET':
        message = ''
        pos_category = request.GET.get('pos_category', None)
        pid = request.GET.get('pid', None)
        # 有分类
        if pos_category:
            if pos_category == 'ann':
                if pid:
                    try:
                        announcement_ = models.Announcement.objects.get(id=int(pid))
                        return render(request, 'gpm/passage.html', locals())
                    except:
                        message = '您访问的文章不存在'
                        return notify_and_jump(request, '/index/passage?pos_category=ann', message)
                else:
                    announcements = models.Announcement.objects.all()
                    if len(announcements) == 0:
                        message = '该分类下目前还没有文章'
                    return render(request, 'gpm/passage.html', locals())

            elif pos_category == 'reg':
                if pid:
                    try:
                        regulation_ = models.Regulation.objects.get(id=int(pid))
                        return render(request, 'gpm/passage.html', locals())
                    except:
                        message = '您访问的文章不存在'
                        return notify_and_jump(request, '/index/passage?pos_category=reg', message)
                else:
                    regulations = models.Regulation.objects.all()
                    if len(regulations) == 0:
                        message = '该分类下目前还没有文章'
                    return render(request, 'gpm/passage.html', locals())
            elif pos_category == 'jou':
                if pid:
                    try:
                        journalism_ = models.Journalism.objects.get(id=int(pid))
                        return render(request, 'gpm/passage.html', locals())
                    except:
                        message = '您访问的文章不存在'
                        return notify_and_jump(request, '/index/passage?pos_category=jou', message)
                else:
                    # print('hello')
                    journalism = models.Journalism.objects.all()
                    if len(journalism) == 0:
                        message = '该分类下目前还没有文章'
                    return render(request, 'gpm/passage.html', locals())
            else:
                message = '您访问的文章不存在'
                return notify_and_jump(request, '/index/passage', message)
        else:
            # 无分类 发布所有分类
            return render(request, 'gpm/passage.html', locals())
    else:
        return notify_and_jump(request, '/passage', '非法访问')


# 问题查看
def question(request):
    # 未登录
    if not request.session.get('is_login', None):
        message = '请登录后操作，谢谢，O(∩_∩)O'
        return notify_and_jump(request, '/login', message)
    # 读取问题
    if request.method == 'GET':
        message = ''
        req_question_id = request.GET.get('qid', None)
        cus_role = request.session.get('cus_role')
        cus_id_str = request.session.get('cus_id_str')
        cus_id_int = request.session.get('cus_id_int')
        if cus_role == 'student':
            student = models.Customer.objects.get(id=int(cus_id_int))
            if student.cus_project_id:
                if req_question_id:
                    try:
                        question = models.Question.objects.get(id=int(req_question_id))
                        if question.que_from_user == cus_id_str:
                            if question.que_replay:
                                answer = models.Answer.objects.get(ans_que_id=int(req_question_id))
                                answer.ans_read = True
                                answer.save()
                                return render(request, 'gpm/question.html', locals())
                            else:
                                return render(request, 'gpm/question.html', locals())
                        else:
                            question = None
                            message = '您没有权限查看此问题'
                            return render(request, 'gpm/question.html', locals())
                    except:
                        message = '您查看的问题不存在'
                        return notify_and_jump(request, '/question', message)
                else:
                    questions = models.Question.objects.filter(que_from_user=cus_id_str)
                    return render(request, 'gpm/question.html', locals())
            else:
                message = '您还没有选择毕业设计课题呢'
                return notify_and_jump(request, '/project', message)

        elif cus_role == 'teacher':
            if req_question_id:
                try:
                    question = models.Question.objects.get(id=int(req_question_id))
                    if question.que_to_user == cus_id_str:
                        # 设为已读
                        question.que_read = True
                        question.save()

                        if question.que_replay:
                            answer = models.Answer.objects.get(ans_que_id=int(req_question_id))
                            return render(request, 'gpm/question.html', locals())
                        return render(request, 'gpm/question.html', locals())
                    else:
                        message = '您没有权限查看此问题'
                        return render(request, 'gpm/question.html', locals())
                except:
                    message = '您查看的问题不存在'
                    return notify_and_jump(request, '/question', message)
            else:
                questions = models.Question.objects.filter(que_to_user=cus_id_str)
                return render(request, 'gpm/question.html', locals())
        else:
            message = '您好像来到了错误的地方'
            return notify_and_jump(request, '/index', message)


    # 处理提交
    elif request.method == 'POST':
        message = ''
        cus_role = request.session.get('cus_role')
        cus_id_str = request.session.get('cus_id_str')
        cus_id_int = request.session.get('cus_id_int')
        pos_message = request.POST.get('pos_message')
        # ('question', pos_message)
        if not pos_message.strip().replace('\n', ''):
            message = '请不要提交空内容'
            return notify_and_jump(request, '/question', message)
        if cus_role == 'student':
            student = models.Customer.objects.get(id=int(cus_id_int))
            if student.cus_project_id:
                cus_project = models.Project.objects.get(id=int(student.cus_project_id))
                question = models.Question()
                question.que_to_user = cus_project.pro_from_user_id
                question.que_from_user = cus_id_str
                question.que_text = pos_message
                question.save()
                message = '问题发送成功'
                return notify_and_jump(request, '/question', message)
            else:
                message = '您还没有选择毕业设计课题呢'
                return notify_and_jump(request, '/project', message)
        elif cus_role == 'teacher':
            pos_message = request.POST.get('pos_message')
            pos_ans_que_id = request.POST.get('pos_ans_que_id')
            question = models.Question.objects.get(id=int(pos_ans_que_id))
            answer = models.Answer()
            answer.ans_from_user = cus_id_str
            answer.ans_que_id = int(pos_ans_que_id)
            answer.ans_to_user = question.que_from_user
            answer.ans_text = pos_message
            answer.save()
            question.que_replay = True
            question.save()
            message = '问题回复成功！'
            return notify_and_jump(request, '/question', message)
        else:
            message = '您好像来到了错误的地方'
            return notify_and_jump(request, '/index', message)


# 密码加密
def hash_code(o_str, salt='UP-UP'):
    o_str += salt
    hash_fun = hashlib.sha256()
    hash_fun.update(o_str.encode())
    return hash_fun.hexdigest()


def project(request):
    # 学生查看课题
    #  教师查看课题
    # 学生查看单个课题
    # 教师发布课题
    # 未登录
    if not request.session.get('is_login', None):
        message = '请登录后操作，谢谢，O(∩_∩)O'
        return notify_and_jump(request, '/login', message)

    if request.method == 'GET':
        message = ''
        req_cus_role = request.session['cus_role']
        req_project_id = request.GET.get('pid', None)
        cus_id_str = request.session['cus_id_str']

        if req_cus_role == 'student':
            # 请求中所请求的课题
            # print(req_project_id)
            # 以选择课程

            # 获取学生选择的课题

            # 学生未选择，可以查看所有，学生已经选择，则只能查看自己的
            # chose a student
            student_ = models.Customer.objects.get(cus_id=cus_id_str)

            cus_project_id = student_.cus_project_id

            # this student has chosen a project
            if req_project_id:
                if cus_project_id:
                    # double has true
                    if cus_project_id == req_project_id:
                        try:
                            cus_project = models.Project.objects.get(id=int(cus_project_id))
                            # render just one project
                            return render(request, 'gpm/project.html', locals())
                        except:
                            message = '没找到您请求的课题'
                            return notify_and_jump(request, '/project', message)
                    else:
                        message = '您没有权限访问该课题'
                        return notify_and_jump(request, '/project', message)

                else:
                    try:
                        cus_project = models.Project.objects.get(id=int(req_project_id))
                        # render just one project
                        return render(request, 'gpm/project.html', locals())
                    except:
                        message = '没找到您请求的课题'
                        return notify_and_jump(request, '/project', message)
            else:
                if cus_project_id:
                    try:
                        cus_project = models.Project.objects.get(id=int(cus_project_id))
                        # render just one project
                        return render(request, 'gpm/project.html', locals())
                    except:
                        message = '没找到您请求的课题'
                        return notify_and_jump(request, '/project', message)
                else:
                    try:
                        cus_projects = models.Project.objects.all()
                        # render just one project
                        return render(request, 'gpm/project.html', locals())
                    except:
                        message = '没找到您请求的课题'
                        return notify_and_jump(request, '/project', message)

        # 教师只能查看自己发布的课题，如果没有发布，则不能查看
        elif req_cus_role == 'teacher':
            # get all projects of theacher
            cus_projects = models.Project.objects.filter(pro_from_user_id=cus_id_str)

            # print(cus_projects)
            if req_project_id:
                try:
                    cus_project = models.Project.objects.get(id=int(req_project_id))
                    if cus_project.pro_from_user_id == cus_id_str:
                        return render(request, 'gpm/project.html', locals())
                    else:
                        message = '您没有权限访问该课题'
                except:
                    message = '该课题不存在'
                return notify_and_jump(request, '/project', message)
            else:
                return render(request, 'gpm/project.html', locals())

        # 管理员可以产看所有的课题
        elif req_cus_role == 'administrator':
            if req_project_id:
                try:
                    cus_project = models.Project.objects.get(id=int(req_project_id))
                    return render(request, 'gpm/project.html', locals())
                except:
                    message = '该课题不存在'
                    return notify_and_jump(request, '/project', message)
            else:
                cus_projects = models.Project.objects.all()
                return render(request, 'gpm/project.html', locals())

    elif request.method == 'POST':
        req_cus_role = request.session['cus_role']
        req_project_id = request.POST.get('chs_project', None)
        cus_id_str = request.session['cus_id_str']
        message = ''
        # print(request.POST)
        # print(req_project_id)
        if req_cus_role == 'student':
            try:
                student = models.Customer.objects.get(cus_id=cus_id_str)
                # print('stu is ok')
                if student.cus_project_id:
                    message = '您已经选择过课题，请不要重复选择'
                    # print('stu pro is ok')

                else:
                    # print('stu pro id is ok')

                    student.cus_project_id = int(req_project_id)
                    student.save()
                    # print('stu pro save  is ok')

                    message = '您的课题选择成功'
            except:
                message = '出了点问题：（'
            return notify_and_jump(request, '/project', message)

        else:
            message = '您的访问不合法'
            return notify_and_jump(request, '/project', message)


def teacher(request):
    # 未登录
    if not request.session.get('is_login', None):
        message = '请登录后操作，谢谢，O(∩_∩)O'
        return notify_and_jump(request, '/login', message)

    cus_role = request.session.get('cus_role', None)
    cus_id_str = request.session.get('cus_id_str', None)

    teacher_ret = None
    if cus_role == 'administrator':
        teachers_ret = models.Customer.objects.filter(cus_role='teacher')
        co = request.GET.get('co', None)
        tea_id = request.GET.get('tea_id', None)
        if co and tea_id:
            if co == 're':
                try:
                    teacher_t = models.Customer.objects.get(cus_id=tea_id)
                    teacher_t.delete()
                    message = '删除成功'
                    return notify_and_jump(request, '/teacher', message)
                except:
                    message = '该用户不存在'
                    return notify_and_jump(request, '/teacher', message)

        # print(teachers_ret)
        return render(request, 'gpm/teacher.html', locals())
    elif cus_role == 'student':
        # 返回用户信息
        cus_id_str = request.session.get('cus_id_str')
        student = models.Customer.objects.get(cus_id=cus_id_str)
        if student.cus_project_id:
            cus_project = models.Project.objects.get(id=int(student.cus_project_id))
            cus_info = models.Customer.objects.get(cus_id=cus_project.pro_from_user_id)
            teacher_ = True
            return render(request, 'gpm/userinfo.html', locals())
        else:
            message = '您还没有选择毕业设计课题呢'
            return notify_and_jump(request, '/project', message)

    else:
        return redirect('/userinfo')


# 进度查看
def schedule(request):
    # 未登录
    if not request.session.get('is_login', None):
        message = '请登录后操作，谢谢，O(∩_∩)O'
        return notify_and_jump(request, '/login', message)
    # 读取问题
    if request.method == 'GET':
        cus_role = request.session['cus_role']
        cus_id_str = request.session['cus_id_str']
        if cus_role == 'student':
            percent = 0
            student = models.Customer.objects.get(cus_id=cus_id_str)
            if student.cus_project_id:
                percent = 33

            up_file = models.ProjectFile.objects.filter(pro_fil_upload_from_user=cus_id_str)
            if up_file:
                percent = 66

            up_eva = models.Evaluate.objects.filter(eva_from_user=cus_id_str)
            if up_file:
                percent = 100
            return render(request, 'gpm/schedule.html', locals())
        else:
            message = '您的访问不合法'
            return notify_and_jump(request, '/login', message)

    else:
        return render(request, 'gpm/schedule.html', locals())


# 教师评价
def evaluate(request):
    if not request.session.get('is_login', None):
        message = '请登录后操作，谢谢，O(∩_∩)O'
        return notify_and_jump(request, '/login', message)
    if request.method == 'POST':
        message = ''
        cus_role = request.session.get('cus_role')
        cus_id_str = request.session.get('cus_id_str')
        cus_id_int = request.session.get('cus_id_int')
        pos_message = request.POST.get('pos_message')
        # print('evaluate', pos_message)
        if not pos_message.strip().replace('\n', ''):
            message = '请不要提交空内容'
            return notify_and_jump(request, '/question', message)
        if cus_role == 'student':
            student = models.Customer.objects.get(id=int(cus_id_int))
            if student.cus_project_id:
                cus_project = models.Project.objects.get(id=int(student.cus_project_id))
                evaluate = models.Evaluate()
                evaluate.eva_to_user = cus_project.pro_from_user_id
                evaluate.eva_from_user = cus_id_str
                evaluate.eva_text = pos_message
                evaluate.save()
                message = '评价教师成功'
                return notify_and_jump(request, '/evaluate', message)
            else:
                message = '您还没有选择毕业设计课题呢'
                return notify_and_jump(request, '/project', message)
        else:
            message = '您的访问不合法'
            return notify_and_jump(request, '/project', message)
    else:
        cus_role = request.session.get('cus_role')
        cus_id_str = request.session.get('cus_id_str')
        cus_id_int = request.session.get('cus_id_int')
        if cus_role == 'student':
            evaluate_ = models.Evaluate.objects.filter(eva_from_user=cus_id_str)
            if evaluate_:
                evaluate_ = evaluate_[0]
            return render(request, 'gpm/evaluate.html', locals())
        elif cus_role == 'teacher':
            evaluates = models.Evaluate.objects.filter(eva_to_user=cus_id_str)
            return render(request, 'gpm/evaluate.html', locals())
        else:
            message = '您的访问不合法'
            return notify_and_jump(request, '/project', message)


# 数据统计
def data(request):
    if not request.session.get('is_login', None):
        message = '请登录后尝试此操作，谢谢！'
        return notify_and_jump(request, '/login', message)
    cus_role = request.session['cus_role']
    if request.method == 'GET':
        if cus_role == 'administrator':
            # 提问数量
            questions = len(models.Question.objects.all())
            questions_ = models.Question.objects.all()
            questions_to_read = len(questions_.filter(que_read=False))
            questions_to_reply = len(questions_.filter(que_replay=False))

            # 项目数量
            projects = len(models.Project.objects.all())

            # 回答数量
            answers = len(models.Answer.objects.all())

            # 答疑率
            try:
                percent_ans = (answers / questions) * 100
            except:
                percent_ans = 100.00  # 学生总数
            students = len(models.Customer.objects.filter(cus_role='student'))
            # 教师总数

            teachers = len(models.Customer.objects.filter(cus_role='teacher'))
            return render(request, 'gpm/data.html', locals())
        else:
            message = '您的访问不合法'
            return notify_and_jump(request, '/login', message)
    else:
        message = '您的访问不合法'
        return notify_and_jump(request, '/login', message)


# 文件管理
def file(request):
    if not request.session.get('is_login', None):
        message = '请登录后尝试此操作，谢谢！'
        return notify_and_jump(request, '/login', message)

    message = ''
    cus_id_str = request.session['cus_id_str']
    cus_name = request.session['cus_name']
    req_cus_role = request.session['cus_role']

    if request.method == 'POST':
        if req_cus_role == 'teacher':
            try:
                project = models.Project.objects.filter(pro_from_user_id=cus_id_str)
                if project:
                    # print('uploading...')
                    all_file_form = form.AllFileForm(request.POST, request.FILES)
                    # print(all_file_form)
                    if all_file_form.is_valid():
                        all_file = models.AllFile()
                        all_file.all_file = all_file_form.cleaned_data['all_file']
                        all_file.all_fil_text = all_file_form.cleaned_data['all_fil_text']
                        all_file.all_fil_upload_from_user = cus_id_str
                        all_file.save()
                        message = '上传成功'
                        return notify_and_jump(request, '/file', message)
                    message = '上传失败'
                    return notify_and_jump(request, '/file', message)
                else:
                    message = '您还没有发布过课题，目前无法上传文件'
                    return notify_and_jump(request, '/file', message)
            except:
                message = '您还没有发布过课题，目前无法上传文件'
                return notify_and_jump(request, '/file', message)

        elif req_cus_role == 'administrator':
            # print('uploading...')
            all_file_form = form.AllFileForm(request.POST, request.FILES)
            # print(all_file_form)
            if all_file_form.is_valid():
                all_file = models.AllFile()
                all_file.all_file = all_file_form.cleaned_data['all_file']
                all_file.all_fil_text = all_file_form.cleaned_data['all_fil_text']
                all_file.all_fil_upload_from_user = cus_id_str
                all_file.save()
                message = '上传成功'
                return notify_and_jump(request, '/file', message)
            message = '上传失败'
            return notify_and_jump(request, '/file', message)
        elif req_cus_role == 'student':
            student = models.Customer.objects.get(cus_id=cus_id_str)
            if student.cus_project_id:
                pro_file_form = form.ProjectFileForm(request.POST, request.FILES)
                if pro_file_form.is_valid():
                    pro_file = models.ProjectFile()
                    # print(pro_file_form)
                    pro_file.pro_file = pro_file_form.cleaned_data['pro_file']
                    pro_file.pro_fil_text = pro_file_form.cleaned_data['pro_fil_text']
                    pro_file.pro_fil_upload_from_user = cus_id_str
                    project_ = models.Project.objects.get(id=int(student.cus_project_id))
                    pro_file.pro_fil_upload_to_user = project_.pro_from_user_id
                    pro_file.save()
                    student.cus_urge = False
                    student.cus_project_file = True
                    student.save()
                message = '毕业设计文件提交成功'
            return notify_and_jump(request, '/index', message)
    else:

        all_files = models.AllFile.objects.all()

        if req_cus_role == 'administrator':
            all_file_form = form.AllFileForm()
            return render(request, 'gpm/file.html', locals())
        elif req_cus_role == 'teacher':
            project = models.Project.objects.filter(pro_from_user_id=cus_id_str)
            if project:
                all_file_form = form.AllFileForm()
            else:
                message = '您还没有发布过课题，目前无法上传文件'
            up_to_me_pf = models.ProjectFile.objects.filter(pro_fil_upload_to_user=cus_id_str)
            # print(up_to_me_pf)
            return render(request, 'gpm/file.html', locals())
        elif req_cus_role == 'student':
            student = models.Customer.objects.get(cus_id=cus_id_str)
            pro_file_form = None
            if student.cus_project_id:
                try:
                    pro_file = models.ProjectFile.objects.filter(pro_fil_upload_from_user=cus_id_str)
                    if pro_file:
                        message = '您已提交过毕业设计文件，目前无法再提交'
                    else:
                        pro_file_form = form.ProjectFileForm()
                    return render(request, 'gpm/file.html', locals())
                except:
                    pro_file_form = form.ProjectFileForm()
                    return render(request, 'gpm/file.html', locals())
            return render(request, 'gpm/file.html', locals())

    return render(request, 'gpm/file.html', locals())


# 文件下载
def uploads(request):
    if not request.session.get('is_login', None):
        message = '请登录后尝试此操作，谢谢！'
        return notify_and_jump(request, '/login', message)
    # uploads
    if request.method == 'GET':
        try:
            file_path = request.path
            download_file = open('./uploads' + file_path, 'rb')
            file_response = FileResponse(download_file)
            file_response['Content-Type'] = 'application/octet-stream'
            file_response['Content-Disposition'] = 'attachment;filename=' + file_path.split('/')[-1]

            return file_response
        except:
            message = '您访问的文件不存在！'
            return notify_and_jump(request, '/index', message)
    else:
        message = '您的访问不合法！'
        return notify_and_jump(request, '/index', message)


def message(request):
    return HttpResponse('666')
