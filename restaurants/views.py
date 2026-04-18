import json

from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ModelViewSet

from shared.common.mixins import AuthMixin
from shared.common.taxonomies import MenuType, PriceType
from restaurants.application.services.dashboard_service import DashboardService
from restaurants.forms import CategoryForm, MenuItemForm, RestaurantForm
from restaurants.models import Category, MenuItem, Restaurant, Table
from restaurants.serializers import (
    CategorySerializer,
    LiteCategorySerializer,
    LiteMenuItemSerializer,
    MenuItemSerializer,
    RestaurantSerializer,
    TableSerializer,
)
from restaurants.tasks import import_menu_items


# ---------------------------------------------------------------------------
# Dashboard page views
# ---------------------------------------------------------------------------

class DashboardPage(AuthMixin, TemplateView):
    template_name = "restaurants/dashboard/chain.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(DashboardService.get_chain_dashboard_context(self.request))
        return ctx


class RestaurantDetailPage(AuthMixin, TemplateView):
    template_name = "restaurants/dashboard/restaurant.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            DashboardService.get_restaurant_overview_context(
                self.request, kwargs["uid"]
            )
        )
        return ctx


class RestaurantTablesPage(AuthMixin, TemplateView):
    template_name = "restaurants/dashboard/tables.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        restaurant = get_object_or_404(Restaurant, uid=kwargs["uid"], chain=self.request.chain)
        ctx["restaurant"] = restaurant
        ctx["tables"] = Table.objects.filter(restaurant=restaurant).order_by("number")
        ctx["user_profile"] = self.request.profile
        ctx["NOTIFY_WS_DATA"] = json.dumps([
            {"rid": str(restaurant.uid), "url": reverse("common:dashboard-order", kwargs={"uid": str(restaurant.uid)})}
        ])
        return ctx


class RestaurantCategoriesPage(AuthMixin, TemplateView):
    template_name = "restaurants/dashboard/categories.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        restaurant = get_object_or_404(Restaurant, uid=kwargs["uid"], chain=self.request.chain)
        ctx["restaurant"] = restaurant
        ctx["categories"] = Category.objects.filter(restaurant=restaurant).order_by("name")
        ctx["user_profile"] = self.request.profile
        ctx["NOTIFY_WS_DATA"] = json.dumps([
            {"rid": str(restaurant.uid), "url": reverse("common:dashboard-order", kwargs={"uid": str(restaurant.uid)})}
        ])
        return ctx


class CategoryCreatePageView(AuthMixin, FormView):
    form_class = CategoryForm
    template_name = "restaurants/dashboard/add_category.html"
    http_method_names = ["get", "post"]

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["restaurant"] = None
        return kw

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["restaurant"] = get_object_or_404(Restaurant, uid=self.kwargs["uid"], chain=self.request.chain)
        ctx["edit_uid"] = self.request.GET.get("uid", "")
        ctx["edit_name"] = self.request.GET.get("name", "")
        ctx["user_profile"] = self.request.profile
        return ctx

    def form_valid(self, form):
        restaurant = get_object_or_404(Restaurant, uid=self.kwargs["uid"], chain=self.request.chain)
        uid = form.cleaned_data.get("uid")
        if uid:
            category = get_object_or_404(Category, uid=uid, restaurant__chain=self.request.chain)
            category.name = form.cleaned_data["name"]
            category.save()
        else:
            Category.objects.create(name=form.cleaned_data["name"], restaurant=restaurant)
        return redirect(reverse("common:restaurant-categories", kwargs={"uid": str(restaurant.uid)}))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class CategoryEditView(AuthMixin, TemplateView):
    template_name = "restaurants/dashboard/edit_category.html"
    http_method_names = ["get", "post"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["category"] = get_object_or_404(Category, uid=kwargs["uid"], restaurant__chain=self.request.chain)
        ctx["user_profile"] = self.request.profile
        return ctx

    def post(self, request, uid, **kwargs):
        category = get_object_or_404(Category, uid=uid, restaurant__chain=request.chain)
        name = request.POST.get("name", "").strip()
        if name:
            category.name = name
            category.save()
        return redirect(reverse("common:dashboard-category", kwargs={"uid": str(category.uid)}))


class MenuItemFormView(AuthMixin, FormView):
    form_class = MenuItemForm
    template_name = "restaurants/dashboard/add_item.html"
    http_method_names = ["get", "post"]

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["category"] = None
        return kw

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["category"] = get_object_or_404(Category, uid=self.kwargs["uid"], restaurant__chain=self.request.chain)
        ctx["user_profile"] = self.request.profile
        ctx["menu_type_choices"] = MenuType.choices
        item_uid = self.request.GET.get("item_uid", "")
        ctx["item"] = get_object_or_404(MenuItem, uid=item_uid, category__restaurant__chain=self.request.chain) if item_uid else None
        return ctx

    def form_valid(self, form):
        category = get_object_or_404(Category, uid=self.kwargs["uid"], restaurant__chain=self.request.chain)
        uid = form.cleaned_data.get("uid")
        fields = ["name", "menu_type", "available", "full_price", "half_price", "description", "ingredients"]
        if uid:
            item = get_object_or_404(MenuItem, uid=uid, category__restaurant__chain=self.request.chain)
            for field in fields:
                setattr(item, field, form.cleaned_data[field])
            item.save()
        else:
            MenuItem.objects.create(category=category, **{k: form.cleaned_data[k] for k in fields})
        return redirect(reverse("common:dashboard-category", kwargs={"uid": str(category.uid)}))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class CategoryDetailPage(AuthMixin, TemplateView):
    template_name = "restaurants/dashboard/category.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, uid=kwargs["uid"], restaurant__chain=self.request.chain)
        menu_items = MenuItem.objects.filter(category=category)
        ctx["category"] = category
        ctx["menu_items"] = menu_items
        ctx["show_half_price"] = menu_items.filter(half_price__gt=0).exists()
        ctx["user_profile"] = self.request.profile
        ctx["menu_type_choices"] = MenuType.choices
        ctx["menu_item_form"] = MenuItemForm(category=category)
        ctx["NOTIFY_WS_DATA"] = json.dumps([
            {"rid": str(category.restaurant.uid), "url": reverse("common:dashboard-order", kwargs={"uid": str(category.restaurant.uid)})}
        ])
        return ctx


class TableMenuPage(TemplateView):
    template_name = "restaurants/table/table.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        table = get_object_or_404(Table, uid=kwargs["table_uid"])
        search = self.request.GET.get("search", "")
        categories = table.restaurant.category_set.order_by("name").prefetch_related(
            Prefetch(
                "menuitem_set",
                queryset=MenuItem.objects.filter(Q(name__icontains=search) | Q(description__icontains=search)),
                to_attr="filtered_items",
            )
        )
        ctx["table"] = table
        ctx["category_data"] = [
            {"category": cat, "menu_items": cat.filtered_items}
            for cat in categories if cat.filtered_items
        ]
        ctx["search"] = search
        return ctx


# ---------------------------------------------------------------------------
# Dashboard CRUD views
# ---------------------------------------------------------------------------

class RestaurantCreateView(AuthMixin, FormView):
    form_class = RestaurantForm
    template_name = "restaurants/dashboard/add_restaurant.html"
    http_method_names = ["get", "post"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["user_profile"] = self.request.profile
        ctx["edit_uid"] = self.request.GET.get("uid", "")
        ctx["edit_name"] = self.request.GET.get("name", "")
        return ctx

    def form_valid(self, form):
        uid = form.cleaned_data.get("uid")
        if uid:
            restaurant = get_object_or_404(Restaurant, uid=uid, chain=self.request.chain)
            restaurant.name = form.cleaned_data["name"]
            restaurant.save()
        else:
            restaurant = Restaurant.objects.create(name=form.cleaned_data["name"], chain=self.request.chain)
        return redirect(reverse("common:dashboard-restaurant", kwargs={"uid": str(restaurant.uid)}))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class RestaurantDeleteView(AuthMixin, TemplateView):
    http_method_names = ["post"]

    def post(self, request, uid, **kwargs):
        restaurant = get_object_or_404(Restaurant, uid=uid, chain=request.chain)
        for category in restaurant.category_set.all():
            category.menuitem_set.all().delete()
            category.delete()
        restaurant.table_set.all().delete()
        restaurant.delete()
        return redirect(reverse("common:dashboard"))


class TableCreateView(AuthMixin, TemplateView):
    http_method_names = ["post"]

    def post(self, request, uid, **kwargs):
        restaurant = get_object_or_404(Restaurant, uid=uid, chain=request.chain)
        Table.objects.create(restaurant=restaurant)
        return redirect(reverse("common:restaurant-tables", kwargs={"uid": uid}))


class TableDeleteView(AuthMixin, TemplateView):
    http_method_names = ["post"]

    def post(self, request, uid, **kwargs):
        restaurant = get_object_or_404(Restaurant, uid=uid, chain=request.chain)
        table = restaurant.table_set.last()
        if table:
            table.delete()
        return redirect(reverse("common:restaurant-tables", kwargs={"uid": uid}))


class CategoryCreateView(AuthMixin, FormView):
    form_class = CategoryForm
    http_method_names = ["post"]

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["restaurant"] = None
        return kw

    def form_valid(self, form):
        restaurant_uid = self.request.POST.get("restaurant_uid")
        uid = form.cleaned_data.get("uid")
        if uid:
            category = get_object_or_404(Category, uid=uid, restaurant__chain=self.request.chain)
            category.name = form.cleaned_data["name"]
            category.save()
            return redirect(reverse("common:dashboard-restaurant", kwargs={"uid": str(category.restaurant.uid)}))
        restaurant = get_object_or_404(Restaurant, uid=restaurant_uid, chain=self.request.chain)
        Category.objects.create(name=form.cleaned_data["name"], restaurant=restaurant)
        return redirect(reverse("common:dashboard-restaurant", kwargs={"uid": restaurant_uid}))

    def form_invalid(self, form):
        return redirect(self.request.META.get("HTTP_REFERER", reverse("common:dashboard")))


class CategoryDeleteView(AuthMixin, TemplateView):
    http_method_names = ["post"]

    def post(self, request, uid, **kwargs):
        category = get_object_or_404(Category, uid=uid, restaurant__chain=request.chain)
        restaurant_uid = str(category.restaurant.uid)
        category.menuitem_set.all().delete()
        category.delete()
        return redirect(reverse("common:dashboard-restaurant", kwargs={"uid": restaurant_uid}))


class CategoryImportView(AuthMixin, TemplateView):
    http_method_names = ["post"]

    def post(self, request, uid, **kwargs):
        restaurant = get_object_or_404(Restaurant, uid=uid, chain=request.chain)
        if not restaurant.category_set.exists():
            import_menu_items(restaurant.id)
        return redirect(reverse("common:restaurant-categories", kwargs={"uid": uid}))


class MenuItemCreateView(AuthMixin, FormView):
    form_class = MenuItemForm
    http_method_names = ["post"]

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["category"] = None
        return kw

    def form_valid(self, form):
        category_uid = self.request.POST.get("category_uid")
        uid = form.cleaned_data.get("uid")
        fields = ["name", "menu_type", "available", "full_price", "half_price", "description", "ingredients"]
        if uid:
            item = get_object_or_404(MenuItem, uid=uid, category__restaurant__chain=self.request.chain)
            for field in fields:
                setattr(item, field, form.cleaned_data[field])
            item.save()
            return redirect(reverse("common:dashboard-category", kwargs={"uid": str(item.category.uid)}))
        category = get_object_or_404(Category, uid=category_uid, restaurant__chain=self.request.chain)
        MenuItem.objects.create(category=category, **{k: form.cleaned_data[k] for k in fields})
        return redirect(reverse("common:dashboard-category", kwargs={"uid": category_uid}))

    def form_invalid(self, form):
        return redirect(self.request.META.get("HTTP_REFERER", reverse("common:dashboard")))


class MenuItemDeleteView(AuthMixin, TemplateView):
    http_method_names = ["post"]

    def post(self, request, uid, **kwargs):
        item = get_object_or_404(MenuItem, uid=uid, category__restaurant__chain=request.chain)
        category_uid = str(item.category.uid)
        item.delete()
        return redirect(reverse("common:dashboard-category", kwargs={"uid": category_uid}))


# ---------------------------------------------------------------------------
# REST API ViewSets
# ---------------------------------------------------------------------------

class RestaurantViewSet(AuthMixin, ModelViewSet):
    lookup_field = "uid"
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        return Restaurant.objects.filter(chain=self.request.chain)

    def perform_create(self, serializer):
        return serializer.save(chain=self.request.chain)

    def destroy(self, request, **kwargs):
        instance = self.get_object()
        for category in instance.category_set.all():
            category.menuitem_set.all().delete()
            category.delete()
        instance.table_set.all().delete()
        return super().destroy(request, **kwargs)

    @action(methods=["POST"], detail=True)
    def import_menu(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.category_set.count():
                raise ValueError("This restaurant already has categories!!")
            import_menu_items(instance.id)
            return Response(status=HTTP_200_OK)
        except Exception as e:
            raise ValidationError(dict(detail=e))

    @action(methods=["DELETE"], detail=True)
    def table(self, request, *args, **kwargs):
        instance = self.get_object()
        table_last = instance.table_set.last()
        if not table_last:
            return Response(status=HTTP_404_NOT_FOUND)
        table_last.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class TableViewSet(ModelViewSet):
    lookup_field = "uid"
    serializer_class = TableSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("restaurant__uid",)
    http_method_names = ("get", "post", "delete")

    def get_queryset(self):
        if self.request.method.upper() == "GET":
            return Table.objects.all()
        return Table.objects.filter(restaurant__chain=self.request.chain).order_by("number")

    @action(methods=["GET"], detail=True)
    def categories(self, request, *args, **kwargs):
        from django.http import Http404
        try:
            instance: Table = self.get_object()
            search_term = request.GET.get("search", "")
            categories = instance.restaurant.category_set.order_by("name").prefetch_related(
                Prefetch(
                    "menuitem_set",
                    queryset=MenuItem.objects.filter(
                        Q(name__icontains=search_term) | Q(description__icontains=search_term)
                    ),
                    to_attr="filtered_menuitems",
                )
            )
            data = {"table": TableSerializer(instance=instance).data, "categories": []}
            for category in categories:
                menu_items = category.filtered_menuitems
                if not menu_items:
                    continue
                data["categories"].append({
                    "category": LiteCategorySerializer(instance=category).data,
                    "has_half_price": sum(i.half_price for i in menu_items) > 0,
                    "menu_items_count": len(menu_items),
                    "menu_items": LiteMenuItemSerializer(instance=menu_items, many=True).data,
                })
            return Response(data=data, status=HTTP_200_OK)
        except Http404:
            raise
        except Exception as e:
            raise ValidationError(dict(detail=e))

    @action(methods=["GET"], detail=True)
    def cart(self, request, *args, **kwargs):
        import json
        from urllib.parse import unquote
        from django.http import Http404
        try:
            instance: Table = self.get_object()
            cart = json.loads(unquote(request.COOKIES.get("cart", "{}")))
            data = {"table": TableSerializer(instance=instance).data, "cart": {}}
            for key, val in cart.items():
                uid, price_type = key.split("/", 1)
                menu_item = MenuItem.objects.filter(uid=uid, available=True, category__restaurant=instance.restaurant).first()
                quantity = val.get("quantity", 0)
                if menu_item and quantity:
                    data["cart"][key] = {
                        "menu_item": LiteMenuItemSerializer(instance=menu_item).data,
                        "price": menu_item.half_price if price_type == PriceType.HALF else menu_item.full_price,
                        "price_type": price_type,
                        "quantity": quantity,
                    }
            return Response(data=data, status=HTTP_200_OK)
        except Http404:
            raise
        except Exception as e:
            raise ValidationError(dict(detail=e))


class CategoryViewSet(AuthMixin, ModelViewSet):
    lookup_field = "uid"
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ("restaurant__uid",)
    search_fields = ("name",)

    def get_queryset(self):
        return Category.objects.filter(restaurant__chain=self.request.chain).order_by("name")


class MenuItemViewSet(AuthMixin, ModelViewSet):
    lookup_field = "uid"
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("category__uid",)
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        if self.request.method.upper() == "GET":
            return MenuItem.objects.all()
        return MenuItem.objects.filter(category__restaurant__chain=self.request.chain)
