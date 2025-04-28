# from django.test import TestCase

# # Create your tests here.
# def warehouse_view(request):
#     warehouse = Warehouse.objects.first()
    
#     # Основной запрос для материалов на складе
#     base_query = MaterialRecord.objects.filter(
#         warehouse=warehouse,
#         construction_object__isnull=True
#     )
    
#     # Обработка перемещения материалов на объект
#     if request.method == 'POST' and 'move_to_object' in request.POST:
#         record_id = request.POST.get('record_id')
#         object_id = request.POST.get('construction_object')
        
#         try:
#             record = MaterialRecord.objects.get(id=record_id, warehouse=warehouse)
#             construction_object = ConstructionObject.objects.get(id=object_id)
            
#             # Создаем новую запись для объекта (как приход)
#             MaterialRecord.objects.create(
#                 material=record.material,
#                 quantity=record.quantity,
#                 unit=record.unit,
#                 price=record.price,
#                 total=record.total,
#                 barcode=record.barcode,
#                 construction_object=construction_object,
#                 operation_type='income',
#                 datetime=timezone.now()
#             )
            
#             # Удаляем запись со склада или помечаем как перемещенную
#             record.delete()  # или record.operation_type = 'outcome'; record.save()
            
#             messages.success(request, 'Материал успешно перемещен на объект')
#             return redirect('warehouse')
            
#         except (MaterialRecord.DoesNotExist, ConstructionObject.DoesNotExist) as e:
#             messages.error(request, 'Ошибка перемещения материала')
    
#     # Обработка поиска по штрих-коду
#     barcode_query = request.GET.get('barcode')
#     if barcode_query:
#         base_query = base_query.filter(barcode__icontains=barcode_query)
    
#     # Обработка параметров фильтрации
#     end_date = timezone.now()
#     start_date = end_date - timedelta(days=30)
    
#     if request.method == 'GET':
#         period = request.GET.get('period', 'custom')
        
#         if period == 'day':
#             start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
#         elif period == 'week':
#             start_date = (end_date - timedelta(days=end_date.weekday())).replace(
#                 hour=0, minute=0, second=0, microsecond=0)
#         elif period == 'month':
#             start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         elif period == 'quarter':
#             current_quarter = (end_date.month - 1) // 3 + 1
#             start_date = datetime(end_date.year, 3 * current_quarter - 2, 1)
#             start_date = timezone.make_aware(start_date.replace(
#                 hour=0, minute=0, second=0, microsecond=0))
#         elif period == 'custom':
#             custom_start = request.GET.get('start_date')
#             custom_end = request.GET.get('end_date')
            
#             if custom_start:
#                 start_date = datetime.strptime(custom_start, '%Y-%m-%d')
#                 start_date = timezone.make_aware(start_date.replace(
#                     hour=0, minute=0, second=0, microsecond=0))
#             if custom_end:
#                 end_date = datetime.strptime(custom_end, '%Y-%m-%d')
#                 end_date = timezone.make_aware(end_date.replace(
#                     hour=23, minute=59, second=59, microsecond=999999))
    
#     # Применяем фильтрацию по дате
#     records = base_query.filter(
#         datetime__gte=start_date,
#         datetime__lte=end_date
#     ).select_related('warehouse', 'unit').order_by('-datetime')
    
#     # Экспорт в Excel
#     if 'export' in request.GET:
#         return generate_warehouse_excel(records, start_date, end_date)
    
#     # Форма для добавления материала
#     form = WarehouseMaterialForm(warehouse=warehouse)
    
#     if request.method == 'POST':
#         form = WarehouseMaterialForm(request.POST, warehouse=warehouse)
#         if form.is_valid():
#             form.save()
#             return redirect('warehouse')
#     # Получаем список объектов для выбора
#     objects = ConstructionObject.objects.all()
    
#     context = {
#         'records': records,
#         'warehouse': warehouse,
#         'form': form,
#         'objects': objects,  # 
#         'start_date': start_date.strftime('%Y-%m-%d'),
#         'end_date': end_date.strftime('%Y-%m-%d'),
#         'selected_period': period,
#     }
#     return render(request, 'core/warehouse.html', context)