from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect


def index(request):
    return render(request, 'blog/index.html')


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    #if request.method == "POST":
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.published_date = timezone.now()
        post.save()
        return redirect('blog.views.post_list')
    else:
        form = PostForm()
    return render(request, 'blog/post_list.html', {'posts': posts, 'form' : form})


def home_page(request):
    return render(request, 'blog/home_page.html')

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
   # posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    post.remove()
    return redirect('blog.views.post_list')


def post_new(request):
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.published_date = timezone.now()
                post.save()
                return redirect('blog.views.post_list')
        else:
            form = PostForm()
        return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
               # post.published_date = timezone.now()
                post.save()
                return redirect('blog.views.post_list')
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form})

