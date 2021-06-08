from collections import Counter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.paginator import Paginator
from django.shortcuts import render

from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout, urls, views
from django.contrib.auth.decorators import login_required

# from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView
from django.views.generic.edit import FormMixin, CreateView, ModelFormMixin

from .form import *
from .models import *
from .decorators import *
from taggit.models import Tag


# Create your views here.
def popular():
    [ i.count() for i in Blog.objects.all() ]
    test = Blog.objects.all().order_by('-comment_count')

def home(request,*args, **kagrs):
    return redirect("/home/")


class Home_View(View):
    template_name = 'index.html'
    queryset = Blog.objects.all().order_by('-created')

    def get(self, request, *args, **kagrs):
        categories = Categories.objects.all()

        data = serializers.serialize('json', self.queryset)
        print('----',data)

        content = {
            'popular': self.queryset.order_by('-comment_count')[0:3],
            'blog': self.queryset[4:14],
            'blog_all': self.queryset,
            'recent': self.queryset[0:4],
            'cat': categories
        }
        return render(request, self.template_name, content)


class Blog_View(ListView):
    paginator_class = Paginator
    paginate_by = 2
    model = Blog
    template_name = "blog.html"
    queryset = Blog.objects.all().order_by('-created')

    def get_queryset(self):
        if self.request.GET.get('search') != None:
            search = self.request.GET.get('search')
            return Blog.objects.filter(title=search).order_by('-created')
        else:
            return Blog.objects.all().order_by('-created')


    def get(self, request,*args, **kagrs):
        self.paginator_class = self.paginator_class(self.get_queryset(), self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = self.paginator_class.get_page(page_number)
        categories = Categories.objects.all()

        content = {
            'blog': self.queryset.order_by('-comment_count')[0:3],
            'blog_all': page_obj,
            'new': self.queryset[0:3],
            'cat': categories
        }
        return render(request, self.template_name, content)


class Blog_Create_View(LoginRequiredMixin, View, ModelFormMixin):
    login_url = '/login/'
    redirect_field_name = 'User'
    template_name = "blog_create.html"

    model = Blog
    form_class = BlogForm

    def get(self, request,*args, **kagrs):
        form = self.get_form_class()
        categories = Categories.objects.all()
        content = {
            'cat': categories,
            'form' : form
        }
        return render(request, self.template_name, content)

    def post(self, request, *args, **kagrs):
        self.user = request.user
        # form = BlogForm( request.POST, request.FILES )
        form = self.get_form()
        if form.is_valid():
            self.form_valid(form)
        else:
            self.form_invalid(form, request)
        return redirect("/user/")

    def form_valid(self, form):
        data = form.cleaned_data
        blog = Blog.objects.create(owner=self.user, title=data['title'], description=data['description'], pic1=data['pic1'])
        blog.categorie.set(data['categorie'])
        return redirect("/user/")

    def form_invalid(self, form, *args, **kwargs):
        print('form invalid ', args, kwargs)
        return HttpResponseRedirect(form)


class Category_View(View):
    template_name = "category.html"
    paginator_class = Paginator
    paginate_by = 2

    def get_queryset(self, slug=None, *args, **kagrs):
        if id != None:
            return Blog.objects.filter(categorie__slug=slug).order_by('-created')
        else:
            return Blog.objects.all().order_by('-created')

    def get(self, request, slug=None, *args, **kagrs):
        self.paginator_class = self.paginator_class(self.get_queryset(slug), self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = self.paginator_class.get_page(page_number)

        categories = Categories.objects.all()
        content = {
            'popular': Blog.objects.all().order_by('-comment_count')[0:4],
            'new_blogs': page_obj,
            'cat': categories
        }
        return render(request, self.template_name, content)


class Detail_View(View):
    template_name = "detail.html"

    def get(self, request, slug=None, *args, **kagrs):
        object = get_object_or_404(Blog, slug=slug)
        categories = Categories.objects.all()
        comment = Comment.objects.filter(blog=object.id).order_by('-created')
        content = {
            'blog': object,
            'commment':comment,
            'cat': categories
        }
        return render(request, self.template_name, content)

    @method_decorator(login_required)
    def post(self, request, *args, **kagrs):
        blog = get_object_or_404(Blog, title=kagrs['slug'])
        owner = None
        if request.user.is_authenticated == True:
            owner = request.user
        description = request.POST.get('description')
        Comment.objects.create(blog=blog, owner=owner,description=description )
        blog.count()
        return HttpResponseRedirect(request.path)


class User_Edit_View(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'User'

    template_name = "useredit.html"

    def get(self, request, *args, **kagrs):
        userr = request.user.blogger
        form = BloggerForm(instance=userr)
        categories = Categories.objects.all()
        content = {
            'form' : form,
            'cat': categories
        }
        return render(request, self.template_name, content)

    def post(self, request, *args, **kagrs):
        userr = request.user.blogger
        form = BloggerForm(request.POST, request.FILES, instance=userr)
        if form.is_valid():
            form.save()
        return redirect("/user/")


class User_View(LoginRequiredMixin, DetailView ):         #   view to detailview
    template_name = "user.html"
    login_url = '/login/'
    redirect_field_name = 'User'
    model = Blogger
    # slug_field = Blogger.slug

    def get_slug_field(self):
        return self.kwargs.get('slug') or self.request.user.blogger.slug

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()).user or self.request.user

    def get_queryset(self):
        return Blog.objects.filter(owner=self.get_object())

    def get(self, request, *args, **kagrs):
        categories = Categories.objects.all()
        content = {
            'blog_all': self.get_queryset(),
            'user': self.get_object(),
            'cat': categories
        }
        return render(request, self.template_name, content)


#TODO       LOGIN - LOGOUT - REGISTER

# def login_view(request,*args, **kagrs):
#     form = LoginForm()
#     if request.method == "POST":
#         un = request.POST.get("username")
#         pw = request.POST.get("password1")
#         user = authenticate(request, username=un, password=pw)
#         print(user,un,pw)
#         if user is not None:
#             login(request, user)
#             return redirect('/home/')
#     content = {
#         "form": form,
#     }
#     return render(request, "login.html", content)

class Register_View(View):
    def get(self, request,*args, **kagrs):
        form = RegisterForm()
        content = {
            "form": form,
            }
        return render(request, "register.html", content)

    def post(self, request, *args, **kagrs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = form.save()
            Blogger.objects.create(user=user)
            login(request, user)
            return redirect("/user/")

# def logoutuser(request , *args , **kagrs):
#     logout(request)
#     return redirect("/login/")



#TODO REMOVED

def about_view(request,*args, **kagrs):
    blog = Blog.objects.all()
    content={
        'blog'  :   blog
    }
    return render(request,"about.html", content )

def contact_view(request,*args, **kagrs):
    blog = Blog.objects.all()
    content={
        'blog'  :   blog
    }
    return render(request,"contact.html", content )

