from .forms import *
from .serializers import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.http import HttpResponse
import json
from rest_framework.response import Response
from rest_framework.decorators import *
from django.forms.models import model_to_dict


def get_template(name):
    return 'forum/' + name + '.html'


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

"""
def handler404(request):
    response = render_to_response('404'), {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response
"""


def index(request):
    return render(request, get_template("index"))


def ask(request):
    return render(request, get_template('ask'))


def search_tag(request, par, pk):
    cur_topic = get_object_or_404(Topic, pk=par)
    tag = Tag.objects.get(pk=pk)
    all_threads = cur_topic.threads.all().order_by('-time_posted')
    returned_threads = []
    for t in all_threads:
        if tag.title in t.tags:
            returned_threads.append(t)

    return render(request, get_template('tag_results'), {'cur_topic': cur_topic, 'threads': returned_threads, 'cur_tag': tag})


def view_topics(request):
    topics = Topic.objects.filter()
    return render(request, get_template('topics'), {'topics': topics})


def tags(request, pk):
    cur_topic = get_object_or_404(Topic, pk=pk)
    tags = Tag.objects.filter(parent=pk).order_by('-uses')  # Or = cur_topic.tags.all
    return render(request, get_template('tags'), {'cur_topic': cur_topic, 'tags': tags})


def is_blocked(request):
    user_ip = get_client_ip(request)
    try:
        response = Blocked.objects.get(address=user_ip)
        return True
    except Blocked.DoesNotExist:
        return False
    except Blocked.MultipleObjectsReturned:
        return True


def thread(request, par, pk):
    cur_thread = get_object_or_404(Thread, pk=pk)
    form = CommentForm(request.POST, request.FILES)
    print(cur_thread.parent)
    if form.is_valid() and not is_blocked(request):
        comment = form.save(commit=False)
        comment.parent = pk
        comment.time_posted = timezone.now()
        comment.author_ip = get_client_ip(request)
        comment.save()
        cur_thread.comments.add(comment)
        return redirect('forum.views.thread', par=par, pk=pk)
    form = CommentForm()
    comments = cur_thread.comments.all().order_by('-time_posted')
    cp = get_object_or_404(Topic, pk=cur_thread.parent)
    return render(request, get_template('thread'), {'cur_thread': cur_thread, 'comments': comments, 'form': form,
                                                    'cur_parent': cp})


def threads(request, pk):
    cur_topic = get_object_or_404(Topic, pk=pk)
    threads_in_topic = cur_topic.threads.all().order_by('-time_posted')
    form = ThreadForm(request.POST, request.FILES)
    if form.is_valid() and not is_blocked(request):
        new_thread = form.save(commit=False)
        try:
            Thread.objects.get(parent=pk, title=new_thread.title)
        except Thread.DoesNotExist:
            new_thread.parent = pk
            new_thread.save()
            tag_set = set()
            for tag in str(new_thread.tags).split(' '):
                tag_set.add(tag)
            for tag in tag_set:
                if tag:
                    try:
                        tag_object = Tag.objects.get(parent=pk, title=tag)
                        tag_object.uses += 1
                    except Tag.DoesNotExist:
                        tag_object = Tag(parent=pk, title=tag, uses=0)
                        tag_object.uses = 1
                    tag_object.save()
                    new_thread.parsed_tags.add(tag_object)
            new_thread.time_posted = timezone.now()
            new_thread.save()
            new_thread.parent = pk

            cur_topic.threads.add(new_thread)
            return redirect('forum.views.threads', pk=pk)
    form = ThreadForm()
    return render(request, get_template('threads'), {'cur_topic': cur_topic, 'threads': threads_in_topic, 'form': form})


def topic(request, pk):
    cur_topic = get_object_or_404(Topic, pk=pk)
    return render(request, get_template('topic'), {'cur_topic': cur_topic})


def home_page(request):
    return render(request, get_template('home_page'))


def counter(request):
    thread_pk = request.GET["pk"]
    cur_ip = get_client_ip(request)
    cur_thread = Thread.objects.get(pk=thread_pk)
    is_new = True
    for user in cur_thread.users.all():
        if user.ip == cur_ip:
            user.last_request = timezone.now()
            user.save()
            is_new = False
        else:
            if (timezone.now() - user.last_request).total_seconds() > 10:
                user.delete()
    if is_new:
        new_user = UserIp(ip=cur_ip, last_request=timezone.now())
        new_user.save()
        cur_thread.users.add(new_user)
        cur_thread.save()
    count = len(cur_thread.users.all())
    data = dict()
    data["count"] = count
    return HttpResponse(json.dumps(data), content_type='application/json')


@api_view(['GET', 'POST'])
def get_comments(request):
    if not is_blocked(request):
        thread_pk = request.GET["pk"]
        cur_thread = Thread.objects.get(pk=thread_pk)
        comments = cur_thread.comments.all().order_by('-time_posted')
        data = []
        for com in comments:
            new_obj = model_to_dict(com)
            for field in new_obj:
                if field == 'time_posted':
                    new_obj[field] = new_obj[field].strftime("%Y/%m/%d %H:%M:%S")
                if field and field != 'time_posted':
                    new_obj[field] = str(new_obj[field])

            data.append(new_obj)
    else:
        data = [{'text': 'YOU ARE BLOCKED AND NOT ALLOWED TO VIEW OR POST ANYTHING', 'time_posted': ''}]
    return Response(json.dumps(data), content_type='application/json')

"""
# def block_user(request):
#     block = BlockUser(request.POST)
#     admin = Admin.objects.get()
#     user = 0
#     if admin.cur_ip == get_client_ip(request):
#         user = 1
#
#     if block.is_valid():
#         ip = block.cleaned_data['user_ip']
#         new_bad = Blocked(address=ip)
#         new_bad.save()
#         Comment.objects.all().filter(author_ip=ip).delete()
#         return redirect('forum.views.block_user')
#
#     block = BlockUser()
#     return render(request, get_template('block_user'), {'blocka': block, 'user':user})

# def admin_login(request):
#     form = PassForm(request.POST)
#     admin = Admin.objects.get()
#
#     if form.is_valid():
#         if form.cleaned_data['password'] == admin.password:
#             print(admin.password)
#             admin.cur_ip = get_client_ip(request)
#             return redirect('forum.views.home_page')
#     form = PassForm()
#     return render(request, get_template('admin_login'), {'form': form})

# class CommentList(APIView):
#     def get(self, request, format=None):
#         thread_pk = request.GET["pk"]
#         cur_thread = Thread.objects.get(pk=thread_pk)
#         comments = cur_thread.comments.all().order_by('-time_posted')
#         serializer = CommentSerializer(comments, many=True)
#         return HttpResponse(json.dumps(serializer.data), content_type='application/json')
#
#     def post(self, request, format=None):
#         serializer = CommentSerializer(data=request.DATA)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         comment = self.get_object(pk)
#         comment.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
# def post_list(request):
#     posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
#     #if request.method == "POST":
#     form = PostForm(request.POST)
#     if form.is_valid():
#         post = form.save(commit=False)
#         post.author = request.user
#         post.published_date = timezone.now()
#         post.save()
#         return redirect('forum.views.post_list')
#     else:
#         form = PostForm()
#     return render(request, get_template('post_list'), {'posts': posts, 'form' : form})
#
#
# def home_page(request):
#     return render(request, get_template('home_page'))
#
# def post_detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     return render(request, get_template('post_detail'), {'post': post})
#
#
# def post_remove(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#    # posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
#     post.remove()
#     return redirect('forum.views.post_list')
#
#
# def post_new(request):
#         if request.method == "POST":
#             form = PostForm(request.POST)
#             if form.is_valid():
#                 post = form.save(commit=False)
#                 post.author = request.user
#                 post.published_date = timezone.now()
#                 post.save()
#                 return redirect('forum.views.post_list')
#         else:
#             form = PostForm()
#         return render(request, get_template('post_edit'), {'form': form})
#
#
# def post_edit(request, pk):
#         post = get_object_or_404(Post, pk=pk)
#         if request.method == "POST":
#             form = PostForm(request.POST, instance=post)
#             if form.is_valid():
#                 post = form.save(commit=False)
#                 post.author = request.user
#                # post.published_date = timezone.now()
#                 post.save()
#                 return redirect('forum.views.post_list')
#         else:
#             form = PostForm(instance=post)
#         return render(request, get_template('post_edit'), {'form': form})

# def comment_edit(request, pk):
#         post = get_object_or_404(Post, pk=pk)
#         if request.method == "POST":
#             form = CommentForm(request.POST, instance=post)
#             if form.is_valid():
#                 post = form.save(commit=False)
#                 post.author = request.user
#                 post.save()
#                 return redirect('forum.views.post_list')
#         else:
#             form = PostForm(instance=post)
#         return render(request, get_template('post_edit'), {'form': form})
"""