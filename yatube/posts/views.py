from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow
from django.core.paginator import Paginator


def index(request):
    title = 'Последние обновления на сайте'
    text = 'Главная страница'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': post_list,
        'title': title,
        'text': text,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    text = 'Вложенная страница'
    title = f'Записи сообщества {group}'
    post_group = group.posts.all()
    paginator = Paginator(post_group, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'posts': post_group,
        'text': text,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    following = (
            request.user.is_authenticated and
            Follow.objects.filter(
                user=request.user,
                author=author
            ).exists())
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts': posts,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_id = get_object_or_404(Post.objects.select_related('author'),
                                id=post_id)
    author_posts = Post.objects.filter(author_id=post_id.author)
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = request.post
        comment.save()
    context = {
        'post_id': post_id,
        'author_posts': author_posts,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
    return render(request,
                  'posts/create_post.html',
                  {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user == post.author and request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.id)
    elif request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    return render(request,
                  'posts/create_post.html',
                  {'form': form, 'is_edit': is_edit, 'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'post': post, 'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (Follow.objects.filter(
            author=author,
            user=request.user
    )
            .exists() or request.user == author
    ):
        return redirect('posts:profile', username=author.username)
    Follow.objects.create(author=author, user=request.user)
    return redirect('posts:profile',  username=author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = Follow.objects.get(author=author, user=user)
    follow.delete()
    return redirect('posts:profile',  username=author.username)
