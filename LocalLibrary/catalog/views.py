from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic, View
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required , permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # New lines for the new tasks
    num_genres = Genre.objects.all().count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,  # new line
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookDetailView(generic.DetailView):
    model = Book


class BookListView(generic.ListView):
    model = Book
    paginate_by = 3


def get_queryset(self):
    return Book.objects.filter(title__icontains='war')[:5]  # Получить 5 книг, содержащих 'war' в заголовке


def get_context_data(self, **kwargs):
    # Call the base implementation first to get the context
    context = super(BookListView, self).get_context_data(**kwargs)
    # Create any data and add it to the context
    context['some_data'] = 'This is just some data'
    return context


def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)
    return render(request, 'catalog/book_detail.html', context={'book': book})


class AuthorListView(generic.ListView):
    model = Author


class AuthorDetailView(generic.DetailView):
    model = Author


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def my_view(request):
    #

    class MyView(LoginRequiredMixin, View, PermissionRequiredMixin):
        permission_required = 'catalog.can_mark_returned'
        permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
        login_url = '/login/'
        redirect_field_name = 'redirect_to'


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )
