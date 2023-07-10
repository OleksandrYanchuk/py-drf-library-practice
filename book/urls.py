from django.urls import include, path
from book.views import BookListCreateView, BookRetrieveUpdateDestroyView


urlpatterns = [
    # Other URLs
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyView.as_view(), name='book-retrieve-update-destroy'),
]

app_name = "book"