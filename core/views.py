from io import BytesIO
from django.shortcuts import render
# def generate_report_excel(queryset, start_date, end_date,):
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')  # или на любую страницу после выхода

def generate_report_excel(queryset, start_date, end_date, request_params):
    # Создаем выходной поток в памяти
    output = BytesIO()
    
    # Создаем Excel writer с помощью xlsxwriter
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book
    
    # Подготовка данных
    data = []
    for record in queryset:
        naive_datetime = record.datetime.replace(tzinfo=None) if record.datetime else datetime.now()
        
        data.append({
            'Дата операции': naive_datetime,
            # 'Тип': 'Операция' if record.is_operations else 'Материал',
            'Объект/Операция': record.construction_object.name if record.construction_object else record.object_is_operations,
            'Наименование': record.material,
            'Количество': float(record.quantity),
            'Ед. изм.': record.unit.short_name if record.unit else '-',
            'Цена за ед.': float(record.price),
            'Сумма': float(record.total),
            'Способ оплаты': record.get_payment_type_display(),
            'Комментарий': record.comment or '-'
        })
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    # Формируем заголовок с информацией о фильтрах
    filter_info = []
    if request_params.get('material_search'):
        filter_info.append(f"Фильтр по материалам: {request_params['material_search']}")
    if request_params.get('record_type'):
        filter_info.append(f"Тип записей: {'операции' if request_params['record_type'] == 'operations' else 'материалы'}")
    if request_params.get('object_search'):
        filter_info.append(f"Поиск по объекту: {request_params['object_search']}")
    
    report_title = (
        "Отчет по материалам и операциям\n"
        f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
    )
    
    if filter_info:
        report_title += "\n".join(filter_info) + "\n"
    # Формируем заголовок с информацией о фильтрах
    # filter_info = []
    # if request_params.get('material_search'):
    #     filter_info.append(f"Фильтр по материалам: {request_params['material_search']}")
    # if request_params.get('record_type'):
    #     filter_info.append(f"Тип записей: {'операции' if request_params['record_type'] == 'operations' else 'материалы'}")
    # if request_params.get('object_search'):
    #     filter_info.append(f"Поиск по объекту: {request_params['object_search']}")
    
    # report_title = (
    #     "Отчет по материалам и операциям\n"
    #     f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
    # )
    
    # if filter_info:
    #     report_title += "\n".join(filter_info) + "\n"
    
    # report_title += (
    #     f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    #     f"Всего записей: {len(df)}"
    # )
    
    # Записываем DataFrame в Excel
    df.to_excel(writer, sheet_name='Отчет', index=False, startrow=4)
    
    # Получаем объект worksheet
    worksheet = writer.sheets['Отчет']
    
    # Форматы ячеек
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#4472C4',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    
    money_format = workbook.add_format({'num_format': '#,##0.00'})
    date_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm'})
    bold_format = workbook.add_format({'bold': True})
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'left',
        'valign': 'vcenter',
        'text_wrap': True,
    })
    
    # Устанавливаем ширину столбцов
    worksheet.set_column('A:A', 18, date_format)  # Дата операции
    worksheet.set_column('B:B', 12)  # Тип
    worksheet.set_column('C:C', 25)  # Объект/Операция
    worksheet.set_column('D:D', 30)  # Наименование
    worksheet.set_column('E:E', 12)  # Количество
    worksheet.set_column('F:F', 10)  # Ед. изм.
    worksheet.set_column('G:G', 12, money_format)  # Цена за ед.
    worksheet.set_column('H:H', 12, money_format)  # Сумма
    worksheet.set_column('I:I', 15)  # Способ оплаты
    worksheet.set_column('J:J', 30)  # Комментарий
    
    # Заголовок отчета
    worksheet.merge_range('A1:J3', report_title, title_format)
    
    # Заголовки столбцов
    for col_num, column_name in enumerate(df.columns.values):
        worksheet.write(4, col_num, column_name, header_format)
    
    # Итоги
    if not df.empty:
        last_row = len(df) + 4
        total_sum = df['Сумма'].sum()
        
        # Формат для итогов
        total_format = workbook.add_format({
            'bold': True,
            'top': 2,
            'num_format': '#,##0.00',
        })
        
        # Статистика
        object_count = df['Объект/Операция'].nunique()
        material_count = df['Наименование'].nunique()
        
        # Итоговая информация
        worksheet.write(last_row + 1, 6, 'ИТОГО:', bold_format)
        worksheet.write(last_row + 1, 7, total_sum, total_format)
        
        worksheet.write(last_row + 3, 0, f"Количество объектов/операций: {object_count}", bold_format)
        worksheet.write(last_row + 4, 0, f"Количество наименований: {material_count}", bold_format)
    
    # Сохраняем Excel файл
    writer.close()
    output.seek(0)
    
    # Формируем HTTP ответ
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Формируем имя файла
    filename = (
        f"Отчет_"
        f"{start_date.strftime('%d.%m.%Y')}_по_{end_date.strftime('%d.%m.%Y')}"
        f"{'_операции' if request_params.get('record_type') == 'operations' else ''}"
        f"{'_материалы' if request_params.get('record_type') == 'materials' else ''}.xlsx"
    )
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
# def generate_report_excel(queryset, start_date, end_date, material_search=None, record_type=None):
#     # Создаем выходной поток в памяти
#     output = BytesIO()
    
#     # Создаем Excel writer с помощью xlsxwriter
#     writer = pd.ExcelWriter(output, engine='xlsxwriter')
#     workbook = writer.book
    
#     # Подготовка данных с преобразованием дат
#     data = []
#     for record in queryset:  # Используем уже отфильтрованный queryset
#         naive_datetime = record.datetime.replace(tzinfo=None) if record.datetime else datetime.now()
        
#         data.append({
#             'Дата операции': naive_datetime,
#             'Объект': record.construction_object.name if record.construction_object else record.object_is_operations,
#             'Материал': record.material,
#             'Количество': float(record.quantity),
#             'Ед. изм.': record.unit.short_name if record.unit else '-',
#             'Цена за ед.': float(record.price),
#             'Сумма': float(record.total),
#             'Способ оплаты': record.get_payment_type_display() or '-',
#             'Тип операции': record.get_operation_type_display(),
#         })
    
#     # Создаем DataFrame
#     df = pd.DataFrame(data)
    
#     # Формируем заголовок с учетом фильтров
#     report_title = (
#         "Детальный отчет по материалам и операциям\n"
#         f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
#     )
    
#     if material_search:
#         report_title += f"Фильтр по материалам: {material_search}\n"
#     if record_type:
#         report_title += f"Тип записей: {'операции' if record_type == 'operations' else 'материалы'}\n"
    
#     # Записываем DataFrame в Excel
#     df.to_excel(writer, sheet_name='Отчет', index=False, startrow=4)
    
#     # Получаем объекты для форматирования
#     worksheet = writer.sheets['Отчет']
    
#     # Форматы ячеек
#     header_format = workbook.add_format({
#         'bold': True,
#         'text_wrap': True,
#         'valign': 'top',
#         'fg_color': '#4472C4',
#         'font_color': 'white',
#         'border': 1,
#         'align': 'center',
#     })
    
#     money_format = workbook.add_format({'num_format': '#,##0.00'})
#     date_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm'})
#     bold_format = workbook.add_format({'bold': True})
#     title_format = workbook.add_format({
#         'bold': True,
#         'font_size': 12,
#         'align': 'left',
#         'valign': 'vcenter',
#         'text_wrap': True,
#     })
    
#     # Устанавливаем ширину столбцов
#     worksheet.set_column('A:A', 18, date_format)
#     worksheet.set_column('B:B', 25)
#     worksheet.set_column('C:C', 30)
#     worksheet.set_column('D:D', 12)
#     worksheet.set_column('E:E', 10)
#     worksheet.set_column('F:F', 12, money_format)
#     worksheet.set_column('G:G', 12, money_format)
#     worksheet.set_column('H:H', 15)
    
#     # Заголовок отчета
#     worksheet.merge_range('A1:H3', report_title, title_format)
    
#     # Заголовки столбцов
#     for col_num, column_name in enumerate(df.columns.values):
#         worksheet.write(4, col_num, column_name, header_format)
    
#     # Итоги
#     if not df.empty:
#         last_row = len(df) + 4
#         total_sum = df['Сумма'].sum()
        
#         total_format = workbook.add_format({
#             'bold': True,
#             'top': 2,
#             'num_format': '#,##0.00',
#         })
        
#         worksheet.write(last_row + 1, 5, 'ИТОГО:', bold_format)
#         worksheet.write(last_row + 1, 6, total_sum, total_format)
    
#     # Сохраняем Excel файл
#     writer.close()
#     output.seek(0)
    
#     # Формируем HTTP ответ
#     response = HttpResponse(
#         output.getvalue(),
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
    
#     filename = (
#         f"Отчет_{start_date.strftime('%d.%m.%Y')}_по_{end_date.strftime('%d.%m.%Y')}.xlsx"
#     )
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
#     return response
# def generate_report_excel(queryset, start_date, end_date, material_search=None, record_type=None ,request_params=None):
#     # Применяем фильтры
#     if request_params:
#         if 'material_search' in request_params:
#             queryset = queryset.filter(material__icontains=request_params['material_search'])
#         if 'record_type' in request_params:
#             if request_params['record_type'] == 'operations':
#                 queryset = queryset.filter(is_operations=True)
#             elif request_params['record_type'] == 'materials':
#                 queryset = queryset.filter(is_operations=False)
    
#     # Создаем выходной поток
#     output = BytesIO()
#     writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
#     # Формируем заголовок с учетом фильтров
#     report_title = (
#         "Отчет по материалам и операциям\n"
#         f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
#     )
    
#     if request_params and 'material_search' in request_params:
#         report_title += f"Фильтр по материалам: {request_params['material_search']}\n"
#     if request_params and 'record_type' in request_params:
#         report_title += f"Тип записей: {'операции' if request_params['record_type'] == 'operations' else 'материалы'}\n"
    
#     # ... остальная часть функции без изменений ...
# # def generate_report_excel(queryset, start_date, end_date):
# #     # Создаем выходной поток в памяти
# #     output = BytesIO()
    
#     # Создаем Excel writer с помощью xlsxwriter
#     # writer = pd.ExcelWriter(output, engine='xlsxwriter')
#     workbook = writer.book
    
#     # Подготовка данных с преобразованием дат
#     data = []
#     for record in queryset:
#         # Преобразуем datetime с временной зоной в наивный datetime
#         naive_datetime = record.datetime.replace(tzinfo=None) if record.datetime else datetime.now()
        
#         data.append({
#             'Дата операции': naive_datetime,
#             'Объект': record.construction_object.name if record.construction_object else record.object_is_operations,
#             'Материал': record.material,
#             'Количество': float(record.quantity),
#             'Ед. изм.': record.unit.short_name if record.unit else '-',
#             'Цена за ед.': float(record.price),
#             'Сумма': float(record.total),
#             'Способ оплаты': record.get_payment_type_display() or '-',
#             # 'Штрих-код': record.barcode or '-',
#             'Тип операции': record.get_operation_type_display(),
#         })
    
#     # Создаем DataFrame
#     df = pd.DataFrame(data)
    
#     # Записываем DataFrame в Excel
#     df.to_excel(writer, sheet_name='Отчет по объектам', index=False, startrow=4)
    
#     # Получаем объекты для форматирования
#     worksheet = writer.sheets['Отчет по объектам']
    
#     # ===== ФОРМАТИРОВАНИЕ =====
    
#     # 1. Форматы ячеек
#     header_format = workbook.add_format({
#         'bold': True,
#         'text_wrap': True,
#         'valign': 'top',
#         'fg_color': '#4472C4',  # Синий цвет фона
#         'font_color': 'white',
#         'border': 1,
#         'align': 'center',
#     })
    
#     money_format = workbook.add_format({'num_format': '#,##0.00'})
#     date_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm'})
#     bold_format = workbook.add_format({'bold': True})
#     title_format = workbook.add_format({
#         'bold': True,
#         'font_size': 12,
#         'align': 'left',
#         'valign': 'vcenter',
#         'text_wrap': True,
#     })
    
#     # 2. Устанавливаем ширину столбцов
#     worksheet.set_column('A:A', 18, date_format)  # Дата операции
#     worksheet.set_column('B:B', 25)  # Объект
#     worksheet.set_column('C:C', 30)  # Материал
#     worksheet.set_column('D:D', 12)  # Количество
#     worksheet.set_column('E:E', 10)  # Ед. изм.
#     worksheet.set_column('F:F', 12, money_format)  # Цена за ед.
#     worksheet.set_column('G:G', 12, money_format)  # Сумма
#     # worksheet.set_column('H:H', 15)  # Штрих-код
#     worksheet.set_column('I:I', 15)  # Тип операции
    
#     # ===== ЗАГОЛОВОК ОТЧЕТА =====
    
#     # 1. Основная информация
#     report_title = (
#         "Детальный отчет по приходу материалов на объекты\n"
#         f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
#         f"Дата формирования отчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
#         f"Всего записей: {len(df)}"
#     )
    
#     worksheet.merge_range('A1:I3', report_title, title_format)
    
#     # 2. Заголовки столбцов
#     for col_num, column_name in enumerate(df.columns.values):
#         worksheet.write(4, col_num, column_name, header_format)
    
#     # ===== ИТОГИ =====
    
#     if not df.empty:
#         last_row = len(df) + 4
        
#         # Итоговая сумма
#         total_sum = df['Сумма'].sum()
        
#         # Формат для итогов
#         total_format = workbook.add_format({
#             'bold': True,
#             'top': 2,
#             'num_format': '#,##0.00',
#         })
        
#         # Подсчет количества объектов
#         object_count = df['Объект'].nunique()
#         material_count = df['Материал'].nunique()
        
#         # Итоговая информация
#         worksheet.write(last_row + 1, 4, 'ИТОГО:', bold_format)
#         worksheet.write(last_row + 1, 5, total_sum, total_format)
        
#         worksheet.write(last_row + 3, 0, f"Количество объектов: {object_count}", bold_format)
#         worksheet.write(last_row + 4, 0, f"Количество материалов: {material_count}", bold_format)
    
#     # Сохраняем Excel файл
#     writer.close()
#     output.seek(0)
    
#     # Создаем HTTP ответ
#     response = HttpResponse(
#         output.getvalue(),
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
    
#     # Формируем имя файла
#     filename = (
#         f"Отчет_по_объектам_"
#         f"{start_date.strftime('%d.%m.%Y')}_по_{end_date.strftime('%d.%m.%Y')}.xlsx"
#     )
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
#     return response


# @login_required
def add_operation(request):
    
    if request.method == 'POST':
        try:
            # Создаем запись операции
            record = MaterialRecord(
                is_operations=True,
                object_is_operations=request.POST.get('object_is_operations'),
                # construction_object_id=request.POST.get('construction_object'),
                material=request.POST.get('material'),
                quantity=Decimal(request.POST.get('quantity', 1)),
                unit_id=request.POST.get('unit'),
                price=Decimal(request.POST.get('price', 0)),
                payment_type=request.POST.get('payment_type'),
                comment=request.POST.get('comment', ''),
                # operation_type='outcome',  # Для операций всегда расход
                # warehouse=Warehouse.objects.get(=4),
                from_Warehouse = False
            )
        #       construction_object__isnull=False,
        # warehouse__isnull=True,
        # from_Warehouse = False,
            
            # Автоматический расчет total при save()
            record.save()
            
            messages.success(request, 'Операция успешно добавлена')
        except Exception as e:
            messages.error(request, f'Ошибка при добавлении операции: {str(e)}')
    
    return redirect('reports')  # Или куда вам нужно перенаправлять
# Create your views here.
# views.py
from django.shortcuts import render
from .decorators import role_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from io import BytesIO
import pandas as pd
import xlsxwriter
from django.http import HttpResponse
from datetime import datetime
def generate_object_excel_report(queryset, construction_object, start_date, end_date):
    # Создаем выходной поток в памяти
    output = BytesIO()
    
    # Создаем Excel writer с помощью xlsxwriter
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book
    
    # Подготовка данных с преобразованием дат
    data = []
    for record in queryset:
        # Преобразуем datetime с временной зоной в наивный datetime
        naive_datetime = record.datetime.replace(tzinfo=None)
        
        data.append({
            'Дата': naive_datetime,
            'Объект': construction_object.name,
            'Материал': record.material,
            'Количество': float(record.quantity),
            'Ед. изм.': record.unit.short_name,
            'Цена за ед.': float(record.price),
            'Сумма': float(record.total),
         'Способ оплаты': record.get_payment_type_display() or '-',
            # 'Штрих-код': record.barcode or '-',
            'Тип операции': record.get_operation_type_display(),
        })
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Записываем DataFrame в Excel
    df.to_excel(writer, sheet_name='Отчет', index=False, startrow=4)
    
    # Получаем объекты для форматирования
    worksheet = writer.sheets['Отчет']
    
    # ===== ФОРМАТИРОВАНИЕ =====
    
    # 1. Форматы ячеек
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#4472C4',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    
    money_format = workbook.add_format({'num_format': '#,##0.00'})
    date_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm'})
    bold_format = workbook.add_format({'bold': True})
    
    # 2. Устанавливаем ширину столбцов
    worksheet.set_column('A:A', 18, date_format)  # Дата
    worksheet.set_column('B:B', 25)  # Объект
    worksheet.set_column('C:C', 30)  # Материал
    worksheet.set_column('D:D', 12)  # Количество
    worksheet.set_column('E:E', 10)  # Ед. изм.
    worksheet.set_column('F:F', 12, money_format)  # Цена за ед.
    worksheet.set_column('G:G', 12, money_format)  # Сумма
    worksheet.set_column('H:H', 15)  # Штрих-код
    worksheet.set_column('I:I', 15)  # Тип операции
    
    # 3. Заголовки столбцов
    for col_num, column_name in enumerate(df.columns.values):
        worksheet.write(4, col_num, column_name, header_format)
    
    # ===== ЗАГОЛОВОК ОТЧЕТА =====
    
    # 1. Основная информация
    report_title = (
        f"Детальный отчет по объекту: {construction_object.name}\n"
        f"Адрес: {construction_object.address}\n"
        # f"Заказчик: {construction_object.client}\n"
        f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
        f"Дата формирования отчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'left',
        'valign': 'vcenter',
        'text_wrap': True,
    })
    
    worksheet.merge_range('A1:I3', report_title, title_format)
    
    # ===== ИТОГИ =====
    
    if not df.empty:
        last_row = len(df) + 4
        total_sum = df['Сумма'].sum()
        
        # Формат для итогов
        total_format = workbook.add_format({
            'bold': True,
            'top': 1,
            'num_format': '#,##0.00',
        })
        
        worksheet.write(last_row + 1, 5, 'ИТОГО:', bold_format)
        worksheet.write(last_row + 1, 6, total_sum, total_format)
        
        # Добавляем информацию об объекте внизу
        worksheet.write(last_row + 3, 0, f"Отчет сформирован для объекта: {construction_object.name}", bold_format)
    
    # Сохраняем Excel файл
    writer.close()
    output.seek(0)
    
    # Создаем HTTP ответ
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Формируем имя файла
    filename = (
        f"Детальный_отчет_{construction_object.name}_"
        f"{start_date.strftime('%d.%m.%Y')}_по_{end_date.strftime('%d.%m.%Y')}.xlsx"
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def generate_object_excel_report_sklad(queryset, construction_object, start_date, end_date):
    # Создаем выходной поток в памяти
    output = BytesIO()
    
    # Создаем Excel writer с помощью xlsxwriter
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book
    
    # Подготовка данных с преобразованием дат
    data = []
    for record in queryset:
        # Преобразуем datetime с временной зоной в наивный datetime
        naive_datetime = record.datetime.replace(tzinfo=None)
        
        data.append({
            'Дата': naive_datetime,
            'Объект': construction_object.name,
            'Материал': record.material,
            'Количество': float(record.quantity),
            'Ед. изм.': record.unit.short_name,
            'Цена за ед.': float(record.price),
            'Сумма': float(record.total),
         'Способ оплаты': record.get_payment_type_display() or '-',
            # 'Штрих-код': record.barcode or '-',
            # 'Тип операции': record.get_operation_type_display(),
        })
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Записываем DataFrame в Excel
    df.to_excel(writer, sheet_name='Отчет', index=False, startrow=4)
    
    # Получаем объекты для форматирования
    worksheet = writer.sheets['Отчет']
    
    # ===== ФОРМАТИРОВАНИЕ =====
    
    # 1. Форматы ячеек
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#4472C4',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    
    money_format = workbook.add_format({'num_format': '#,##0.00'})
    date_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm'})
    bold_format = workbook.add_format({'bold': True})
    
    # 2. Устанавливаем ширину столбцов
    worksheet.set_column('A:A', 18, date_format)  # Дата
    worksheet.set_column('B:B', 25)  # Объект
    worksheet.set_column('C:C', 30)  # Материал
    worksheet.set_column('D:D', 12)  # Количество
    worksheet.set_column('E:E', 10)  # Ед. изм.
    worksheet.set_column('F:F', 12, money_format)  # Цена за ед.
    worksheet.set_column('G:G', 12, money_format)  # Сумма
    worksheet.set_column('H:H', 15)  # Штрих-код
    worksheet.set_column('I:I', 15)  # Тип операции
    
    # 3. Заголовки столбцов
    for col_num, column_name in enumerate(df.columns.values):
        worksheet.write(4, col_num, column_name, header_format)
    
    # ===== ЗАГОЛОВОК ОТЧЕТА =====
    
    # 1. Основная информация
    report_title = (
        f"Детальный отчет по объекту: {construction_object.name}\n"
        f"Адрес: {construction_object.address}\n"
        # f"Заказчик: {construction_object.client}\n"
        f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
        f"Дата формирования отчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'left',
        'valign': 'vcenter',
        'text_wrap': True,
    })
    
    worksheet.merge_range('A1:I3', report_title, title_format)
    
    # ===== ИТОГИ =====
    
    if not df.empty:
        last_row = len(df) + 4
        total_sum = df['Сумма'].sum()
        
        # Формат для итогов
        total_format = workbook.add_format({
            'bold': True,
            'top': 1,
            'num_format': '#,##0.00',
        })
        
        worksheet.write(last_row + 1, 5, 'ИТОГО:', bold_format)
        worksheet.write(last_row + 1, 6, total_sum, total_format)
        
        # Добавляем информацию об объекте внизу
        worksheet.write(last_row + 3, 0, f"Отчет сформирован для объекта: {construction_object.name}", bold_format)
    
    # Сохраняем Excel файл
    writer.close()
    output.seek(0)
    
    # Создаем HTTP ответ
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Формируем имя файла
    filename = (
        f"Детальный_отчет_{construction_object.name}_"
        f"{start_date.strftime('%d.%m.%Y')}_по_{end_date.strftime('%d.%m.%Y')}.xlsx"
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, "Для доступа необходимо авторизоваться")
        return redirect('login')
    
    context = {
        'username': request.user.username,
        'is_admin': request.user.is_superuser,
    }
    return render(request, 'core/dashboard.html', context)
@role_required('admin')
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@role_required('accountant')
def accountant_dashboard(request):
    return render(request, 'accountant_dashboard.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ConstructionObject, ConstructionObjectOfWarehouse, MaterialRecord, StorageLocation, Unit
from django.db.models import Q
import pandas as pd
from django.http import HttpResponse

@login_required
def objects_view(request):
    # Фильтрация
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    objects = ConstructionObject.objects.all()
    
    if query:
        objects = objects.filter(
            Q(name__icontains=query) | 
            Q(address__icontains=query) 
        )
    
    if status_filter:
        objects = objects.filter(status=status_filter)
    
    # Генерация отчета Excel
    if 'export' in request.GET:
        return generate_excel_report(objects)
    
    # Получение материалов для объектов
    materials = MaterialRecord.objects.filter(
        construction_object__isnull=False
    ).select_related('construction_object', 'unit')
    
    context = {
        'objects': objects,
        'materials': materials,
        'search_query': query,
        'status_filter': status_filter,
    }
    return render(request, 'core/objects.html', context)

def generate_excel_report(objects):
    data = []
    for obj in objects:
        materials = MaterialRecord.objects.filter(construction_object=obj)
        for mat in materials:
            data.append({
                'Объект': obj.name,
                'Адрес': obj.address,
                
              
                'Материал': mat.material,
                'Количество': mat.quantity,
                'Ед. изм.': mat.unit.short_name,
                'Цена': mat.price,
                'Сумма': mat.total,
                
                'Тип операции': mat.get_operation_type_display(),
                'Дата': mat.datetime.strftime('%d.%m.%Y %H:%M'),
            })
    
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="objects_report.xlsx"'
    df.to_excel(response, index=False)
    return response


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from .models import MaterialRecord, ConstructionObject
from datetime import datetime, timedelta
import pandas as pd
from django.http import HttpResponse

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from .models import MaterialRecord, ConstructionObject
from datetime import datetime, timedelta
import pandas as pd
from django.db.models.functions import Lower
from django.http import HttpResponse
@login_required
def reports_view(request):
    # Базовый запрос
    base_query = MaterialRecord.objects.filter(
        Q(construction_object__isnull=False) | Q(is_operations=True),
        Q(warehouse__isnull=True) | Q(is_operations=True),
        from_Warehouse=False
    )

    units = Unit.objects.all()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Обработка параметров фильтрации
    if request.method == 'GET':
        period = request.GET.get('period', 'custom')
        
        # Обработка периода (ваш существующий код)
        if period == 'day':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = end_date - timedelta(days=end_date.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'month':
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'quarter':
            current_quarter = (end_date.month - 1) // 3 + 1
            start_date = datetime(end_date.year, 3 * current_quarter - 2, 1)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'custom':
            custom_start = request.GET.get('start_date')
            custom_end = request.GET.get('end_date')
            if custom_start:
                start_date = datetime.strptime(custom_start, '%Y-%m-%d')
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            if custom_end:
                end_date = datetime.strptime(custom_end, '%Y-%m-%d')
                end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Применяем все фильтры последовательно
        filtered_query = base_query
        
        # Поиск по объектам
        object_search = request.GET.get('object_search')
        if object_search:
            filtered_query = filtered_query.filter(
                Q(construction_object__name__icontains=object_search) |
                Q(object_is_operations__icontains=object_search)
            )
        
        # Поиск по материалам
        material_search = request.GET.get('material_search')
        if material_search:
            filtered_query = filtered_query.filter(material__icontains=material_search)
        
        # Фильтр по типу записи
        record_type = request.GET.get('record_type')
        if record_type == 'operations':
            filtered_query = filtered_query.filter(is_operations=True)
        elif record_type == 'materials':
            filtered_query = filtered_query.filter(is_operations=False)

        # Фильтрация по дате (должна быть последней)
        records = filtered_query.filter(
            datetime__gte=start_date,
            datetime__lte=end_date
        ).select_related('construction_object', 'unit')

        # Экспорт в Excel (должен быть перед рендерингом шаблона)
        if 'export' in request.GET:
            return generate_report_excel(
                records,  # Уже полностью отфильтрованный queryset
                start_date, 
                end_date,
                request.GET  # Передаем все параметры фильтрации
            )

    # Группировка данных для сводной таблицы
    summary = records.values(
        'construction_object__name',
        'object_is_operations',
        'material',
        'is_operations'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sum=Sum('total')
    ).order_by('construction_object__name', 'material')

    context = {
        'records': records,
        'report':True,
        'objects': ConstructionObject.objects.all(),
        'summary': summary,
        'units': units,
        'all_objects': ConstructionObject.objects.all(),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'selected_period': period,
        'record_type': request.GET.get('record_type', 'all'),
    }
    return render(request, 'core/reports.html', context)
# @login_required
# def reports_view(request):
#     # Базовый запрос
#     base_query = MaterialRecord.objects.filter(
#         Q(construction_object__isnull=False) | Q(is_operations=True),
#         Q(warehouse__isnull=True) | Q(is_operations=True),
#         from_Warehouse=False
#     )

#     units = Unit.objects.all()
#     end_date = datetime.now()
#     start_date = end_date - timedelta(days=30)
#     # Экспорт в Excel
    
#     # Обработка параметров фильтрации
#     if request.method == 'GET':
#         period = request.GET.get('period', 'custom')
#         # ... существующая логика периода ...
        
#         # Поиск по объектам
#         object_search = request.GET.get('object_search')
#         if object_search:
#             base_query = base_query.filter(
#                 Q(construction_object__name__icontains=object_search) |
#                 Q(object_is_operations__icontains=object_search)
#             )
#         # Применяем фильтрацию по дате
#         records = base_query.filter(
#             datetime__gte=start_date,
#             datetime__lte=end_date
#         ).select_related('construction_object', 'unit')
        
#         # Экспорт в Excel
#         if 'export' in request.GET:
#             return generate_report_excel(
#                 records,  # Уже отфильтрованный queryset
#                 start_date, 
#                 end_date,
#                 material_search=request.GET.get('material_search'),
#                 record_type=request.GET.get('record_type')
#             )
#         # Поиск по материалам
#         material_search = request.GET.get('material_search')
#         if material_search:
#             base_query = base_query.filter(material__icontains=material_search)
        
#         # Фильтр по типу записи (материал/операция)
#         record_type = request.GET.get('record_type')
#         if record_type == 'operations':
#             base_query = base_query.filter(is_operations=True)
#         elif record_type == 'materials':
#             base_query = base_query.filter(is_operations=False)
    
#     # Применяем фильтрацию по дате
#     records = base_query.filter(
#         datetime__gte=start_date,
#         datetime__lte=end_date
#     ).select_related('construction_object', 'unit')
#     # if 'export' in request.GET:
#     #     # Передаем все параметры фильтрации
#     #     return generate_report_excel(
#     #         records,  # Уже отфильтрованный queryset
#     #         start_date, 
#     #         end_date,
#     #         material_search=request.GET.get('material_search'),
#     #         record_type=request.GET.get('record_type')
#     #     )
#     # Группировка данных для сводной таблицы
#     summary = records.values(
#         'construction_object__name',
#         'object_is_operations',
#         'material',
#         'is_operations'
#     ).annotate(
#         total_quantity=Sum('quantity'),
#         total_sum=Sum('total')
#     ).order_by('construction_object__name', 'material')

#     context = {
#         'records': records,
#         'objects': ConstructionObject.objects.all(),
#         'summary': summary,
#         'units': units,
#         'all_objects': ConstructionObject.objects.all(),
#         'start_date': start_date.strftime('%Y-%m-%d'),
#         'end_date': end_date.strftime('%Y-%m-%d'),
#         'selected_period': period,
#         'record_type': request.GET.get('record_type', 'all'),
#     }
#     return render(request, 'core/reports.html', context)
# @login_required
# def reports_view(request):
#     # Базовый запрос - только записи с объектом и без склада
#     base_query = MaterialRecord.objects.filter(
#         # construction_object__isnull=False,
#     from_Warehouse=False)
#     # 
#     print(base_query)
#     base_query.filter(Q(construction_object__isnull=False) | Q(is_operations=True))
#     base_query.filter(Q(warehouse__isnull=True) | Q(is_operations=True))
#     # base_query = MaterialRecord.objects.filter(
#     #     construction_object__isnull=False,
#     #     warehouse__isnull=True or is_operations__isnul=True,
#     #     from_Warehouse = False,
#         # operation_type='income'  # Перенес фильтр по типу операции в базовый запрос
    
#     units = Unit.objects.all()
#     # Определение периода по умолчанию (последние 30 дней)
#     end_date = datetime.now()
#     start_date = end_date - timedelta(days=30)
    
#     # Обработка параметров фильтрации
#     if request.method == 'GET':
#         period = request.GET.get('period', 'custom')
        
#         if period == 'day':
#             start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
#         elif period == 'week':
#             start_date = end_date - timedelta(days=end_date.weekday())
#             start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
#         elif period == 'month':
#             start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         elif period == 'quarter':
#             current_quarter = (end_date.month - 1) // 3 + 1
#             start_date = datetime(end_date.year, 3 * current_quarter - 2, 1)
#             start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
#         elif period == 'custom':
#             custom_start = request.GET.get('start_date')
#             custom_end = request.GET.get('end_date')
            
#             if custom_start:
#                 start_date = datetime.strptime(custom_start, '%Y-%m-%d')
#                 start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
#             if custom_end:
#                 end_date = datetime.strptime(custom_end, '%Y-%m-%d')
#                 end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

#     # Применяем фильтрацию по дате
#     records = base_query.filter(
#         datetime__gte=start_date,
#         datetime__lte=end_date
#     ).select_related('construction_object', 'unit')
    
#     # Дополнительная фильтрация по объекту, если указана
#     object_filter = request.GET.get('object')
#     if object_filter:
#         records = records.filter(construction_object_id=object_filter)
    
#     # Группировка данных для сводной таблицы
#     summary = records.values(
#         'construction_object__name',
#         'material',
#         'is_operations',
#         'object_is_operations'
#     ).annotate(
#         total_quantity=Sum('quantity'),
#         total_sum=Sum('total')
#     ).order_by('construction_object__name', 'material')
    
#     # Получение списка объектов для фильтра
#     all_objects = ConstructionObject.objects.all()
    
#     # Экспорт в Excel
#     if 'export' in request.GET:
#         return generate_report_excel(records, start_date, end_date)
    
#     objects = ConstructionObject.objects.all()
#     search_query = request.GET.get('object_search')
#     if search_query:
#     # Удаляем лишние пробелы и приводим к нижнему регистру для более гибкого поиска
#         objects = objects.filter(name__icontains=search_query)
#             # records = records.filter(
#     # construction_object = search_query
#         # )
    
#     # if query:
#     #     objects = objects.filter(
#     #         Q(name__icontains=query) | 
#     #         Q(address__icontains=query) 
#     #     )
#     context = {
#         'records': records,
#         'objects': objects,
#         'summary': summary,
#         'units': units,
#         'all_objects': all_objects,
#         'selected_object': int(object_filter) if object_filter else None,
#         'start_date': start_date.strftime('%Y-%m-%d'),
#         'end_date': end_date.strftime('%Y-%m-%d'),
#         'selected_period': period,
#     }
#     return render(request, 'core/reports.html', context)


@login_required
def reports_view_skalda(request):
    # Базовый запрос - только записи с объектом и без склада
    base_query = StorageLocation.objects.filter(
        construction_object__isnull=False,
        warehouse__isnull=True,
        # from_Warehouse = False,
        # operation_type='income'  # Перенес фильтр по типу операции в базовый запрос
    )
    
    # Определение периода по умолчанию (последние 30 дней)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Обработка параметров фильтрации
    if request.method == 'GET':
        period = request.GET.get('period', 'custom')
        
        if period == 'day':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = end_date - timedelta(days=end_date.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'month':
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'quarter':
            current_quarter = (end_date.month - 1) // 3 + 1
            start_date = datetime(end_date.year, 3 * current_quarter - 2, 1)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'custom':
            custom_start = request.GET.get('start_date')
            custom_end = request.GET.get('end_date')
            
            if custom_start:
                start_date = datetime.strptime(custom_start, '%Y-%m-%d')
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            if custom_end:
                end_date = datetime.strptime(custom_end, '%Y-%m-%d')
                end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Применяем фильтрацию по дате
    records = base_query.filter(
        datetime__gte=start_date,
        datetime__lte=end_date
    ).select_related('construction_object', 'unit')
    
    # Дополнительная фильтрация по объекту, если указана
    object_filter = request.GET.get('object')
    if object_filter:
        records = records.filter(construction_object_id=object_filter)
    
    # Группировка данных для сводной таблицы
    summary = records.values(
        'construction_object__name',
        'material'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sum=Sum('total')
    ).order_by('construction_object__name', 'material')
    
    # Получение списка объектов для фильтра
    all_objects = ConstructionObjectOfWarehouse.objects.all()
    
    # Экспорт в Excel
    if 'export' in request.GET:
        return generate_report_excel(records, start_date, end_date)
    objects = ConstructionObjectOfWarehouse.objects.all()
    
    # if query:
    #     objects = objects.filter(
    #         Q(name__icontains=query) | 
    #         Q(address__icontains=query) 
    #     )
    context = {
        "backwarehouse":True,
        'records': records,
        'objects': objects,
        'summary': summary,
        'all_objects': all_objects,
        'selected_object': int(object_filter) if object_filter else None,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'selected_period': period,
    }
    return render(request, 'sklad/objects_sklada.html', context)
# def generate_report_excel(queryset, start_date, end_date):
#     data = []
#     for record in queryset:
#         data.append({
#             'Дата': record.datetime.strftime('%d.%m.%Y %H:%M'),
#             'Объект': record.construction_object.name,
#             'Материал': record.material,
#             'Количество': record.quantity,
#             'Ед. изм.': record.unit.short_name,
#             'Цена': record.price,
#             'Сумма': record.total,
#             'Штрих-код': record.barcode,
#         })
    
#     df = pd.DataFrame(data)
#     response = HttpResponse(content_type='application/ms-excel')
#     filename = f"objects_report_{start_date.date()}_to_{end_date.date()}.xlsx"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     df.to_excel(response, index=False)
#     return response





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from .models import MaterialRecord, Warehouse
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import ObjectMaterialFormSklad, WarehouseMaterialForm
import pandas as pd
from django.http import HttpResponse

# @login_required
# def warehousewarehouse_view_view(request):
#     # Получаем склад по умолчанию (или первый созданный)
#     warehouse = Warehouse.objects.first()
    
#     # Базовый запрос для склада
#     base_query = MaterialRecord.objects.filter(
#         warehouse=warehouse,
#         construction_object__isnull=True
#     )
    
#     # Обработка фильтрации по дате
#     end_date = timezone.now()
#     start_date = end_date - timedelta(days=30)
    
#     if request.method == 'GET':
#         period = request.GET.get('period', 'custom')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from .models import MaterialRecord, ConstructionObject, Warehouse, HistoryOdWarehouse
# @login_required
# def warehouse_view(request):
#     warehouse = Warehouse.objects.first()
#     base_query = MaterialRecord.objects.filter(
#         warehouse=warehouse,
#         construction_object__isnull=True
#     ).select_related('unit', 'warehouse')
    
#     if request.method == 'POST':
#         # Обработка добавления количества
#         if 'add_quantity' in request.POST:
#             record_id = request.POST.get('record_id')
#             quantity_to_add = request.POST.get('add_quantity', '').strip()
            
#             try:
#                 record = MaterialRecord.objects.get(id=record_id, warehouse=warehouse)
                
#                 # Проверка на пустое значение
#                 if not quantity_to_add:
#                     messages.error(request, 'Пожалуйста, введите количество')
#                     return redirect('warehouse')
                
#                 # Заменяем запятую на точку и удаляем пробелы
#                 quantity_str = quantity_to_add.replace(',', '.').replace(' ', '')
                
#                 try:
#                     quantity_to_add = Decimal(quantity_str)
#                 except InvalidOperation:
#                     messages.error(request, 'Некорректный формат числа')
#                     return redirect('warehouse')
                
#                 if quantity_to_add <= 0:
#                     messages.error(request, 'Количество должно быть больше нуля')
#                     return redirect('warehouse')
                
#                 # Создаем запись в истории
#                 HistoryOdWarehouse.objects.create(
#                     operation_type='income',
#                     datetime=timezone.now(),
#                     warehouse=warehouse,
#                     construction_object=None,
#                     payment_type=record.payment_type,
#                     material=record.material,
#                     unit=record.unit,
#                     barcode=record.barcode,
#                     quantity=quantity_to_add,
#                     price=record.price,
#                     total=quantity_to_add * record.price,
#                     comment="Добавлено количество к существующему материалу"
#                 )
                
#                 # Обновляем исходную запись
#                 record.quantity += quantity_to_add
#                 record.total = record.quantity * record.price
#                 record.save()
                
#                 messages.success(request, f'Добавлено {quantity_to_add}{record.unit.short_name} материала "{record.material}"')
#                 return redirect('warehouse')
            
#             except MaterialRecord.DoesNotExist:
#                 messages.error(request, 'Запись не найдена')
#             except Exception as e:
#                 messages.error(request, f'Ошибка: {str(e)}')
        
        # Остальная обработка POST-запросов...
    
    # Остальной код представления...
@login_required
def warehouse_view(request):
    warehouse = Warehouse.objects.first()
    base_query = MaterialRecord.objects.filter(
        warehouse=warehouse,
        construction_object__isnull=True
    ).select_related('unit', 'warehouse')
    
    barcode = request.GET.get('barcode')
    if barcode:
        base_query = base_query.filter(barcode=barcode)
        
    if request.method == 'POST':
        # Обработка добавления количества
        if 'add_quantity' in request.POST:
            print(f"Add quantity POST data: {request.POST}")
            record_id = request.POST.get('record_id')
            quantity_to_add = request.POST.get('add_quantity', '').strip()
            
            try:
                record = MaterialRecord.objects.get(id=record_id, warehouse=warehouse)
                
                # Проверка на пустое значение
                if not quantity_to_add:
                    messages.error(request, 'Пожалуйста, введите количество для добавления')
                    return redirect('warehouse')
                
                # Заменяем запятую на точку и удаляем пробелы
                quantity_str = quantity_to_add.replace(',', '.').replace(' ', '')
                
                try:
                    quantity_to_add = Decimal(quantity_str)
                except InvalidOperation:
                    messages.error(request, 'Некорректный формат числа. Используйте цифры и точку/запятую для десятичных')
                    return redirect('warehouse')
                
                if quantity_to_add <= 0:
                    messages.error(request, 'Количество должно быть больше нуля')
                    return redirect('warehouse')
                
                # Создаем запись в истории
                HistoryOdWarehouse.objects.create(
                    operation_type='income',
                    datetime=timezone.now(),
                    warehouse=warehouse,
                    construction_object=None,
                    payment_type=record.payment_type,
                    material=record.material,
                    unit=record.unit,
                    barcode=record.barcode,
                    quantity=quantity_to_add,
                    price=record.price,
                    total=quantity_to_add * record.price,
                    comment="Добавлено количество к существующему материалу"
                )
                
                # Обновляем исходную запись
                record.quantity += quantity_to_add
                record.total = record.quantity * record.price
                record.save()
                
                messages.success(request, f'Добавлено {quantity_to_add}{record.unit.short_name} материала "{record.material}"')
                return redirect('warehouse')
            
            except MaterialRecord.DoesNotExist:
                messages.error(request, 'Запись не найдена')
            except Exception as e:
                messages.error(request, f'Ошибка при добавлении количества: {str(e)}')
        
        # Обработка перемещения материалов на объект
        
        elif 'move_to_objects_klada' in request.POST:
            record_id = request.POST.get('record_id')
            object_id = request.POST.get('construction_object')
            quantity_to_move = request.POST.get('quantity', '').strip()
            
            try:
                record = MaterialRecord.objects.get(id=record_id, warehouse=warehouse)
                construction_object = ConstructionObjectOfWarehouse.objects.get(id=object_id)
                
                # Проверка на пустое значение
                if not quantity_to_move:
                    messages.error(request, 'Пожалуйста, введите количество для перемещения')
                    return redirect('warehouse')
                
                # Преобразуем количество в Decimal
                try:
                    quantity_to_move = Decimal(quantity_to_move.replace(',', '.'))
                except InvalidOperation:
                    messages.error(request, 'Некорректный формат количества для перемещения')
                    return redirect('warehouse')
                
                # Проверки
                if quantity_to_move <= 0:
                    messages.error(request, 'Количество должно быть больше нуля')
                    return redirect('warehouse')
                    
                if quantity_to_move > record.quantity:
                    messages.error(request, f'Недостаточно материала (доступно: {record.quantity})')
                    return redirect('warehouse')
                
                # Создаем запись на объекте
                StorageLocation.objects.create(
                    # operation_type='income',
                    datetime=timezone.now(),
                    construction_object=construction_object,
                    warehouse=None,
                    payment_type=record.payment_type,
                    material=record.material,
                    unit=record.unit,
                    barcode=record.barcode,
                    quantity=quantity_to_move,
                    price=record.price,
                    total=quantity_to_move * record.price,
                    from_Warehouse=True,
                    comment=f"Перемещено со склада {warehouse.name}"
                )
                
                # Обновляем исходную запись
                if quantity_to_move == record.quantity:
                     # Создаем запись расхода на складе
                    HistoryOdWarehouse.objects.create(
                        operation_type='outcome',
                        datetime=timezone.now(),
                        warehouse=warehouse,
                        # construction_object=construction_object,
                        payment_type=record.payment_type,
                        material=record.material,
                        unit=record.unit,
                        barcode=record.barcode,
                        quantity=quantity_to_move,
                        price=record.price,
                        total=quantity_to_move * record.price,
                        comment=f"Перемещено на объект склада {construction_object.name}"
                    )
                    record.delete()
                else:
                    # Создаем запись расхода на складе
                    HistoryOdWarehouse.objects.create(
                        operation_type='outcome',
                        datetime=timezone.now(),
                        warehouse=warehouse,
                        # construction_object=construction_object,
                        payment_type=record.payment_type,
                        material=record.material,
                        unit=record.unit,
                        barcode=record.barcode,
                        quantity=quantity_to_move,
                        price=record.price,
                        total=quantity_to_move * record.price,
                        comment=f"Перемещено на объект склада {construction_object.name}"
                    )
                    
                    # Обновляем исходную запись
                    record.quantity -= quantity_to_move
                    record.total = record.quantity * record.price
                    record.save()
                
                messages.success(request, f'Материал "{record.material}" перемещен на объект "{construction_object.name}"')
                return redirect('warehouse')
            
            except Exception as e:
                messages.error(request, f'Ошибка при перемещении: {str(e)}')
        
        elif 'move_to_object' in request.POST:
            record_id = request.POST.get('record_id')
            object_id = request.POST.get('construction_object')
            quantity_to_move = request.POST.get('quantity', '').strip()
            
            try:
                record = MaterialRecord.objects.get(id=record_id, warehouse=warehouse)
                construction_object = ConstructionObject.objects.get(id=object_id)
                
                # Проверка на пустое значение
                if not quantity_to_move:
                    messages.error(request, 'Пожалуйста, введите количество для перемещения')
                    return redirect('warehouse')
                
                # Преобразуем количество в Decimal
                try:
                    quantity_to_move = Decimal(quantity_to_move.replace(',', '.'))
                except InvalidOperation:
                    messages.error(request, 'Некорректный формат количества для перемещения')
                    return redirect('warehouse')
                
                # Проверки
                if quantity_to_move <= 0:
                    messages.error(request, 'Количество должно быть больше нуля')
                    return redirect('warehouse')
                    
                if quantity_to_move > record.quantity:
                    messages.error(request, f'Недостаточно материала (доступно: {record.quantity})')
                    return redirect('warehouse')
                
                # Создаем запись на объекте
                MaterialRecord.objects.create(
                    operation_type='income',
                    datetime=timezone.now(),
                    construction_object=construction_object,
                    warehouse=None,
                    payment_type=record.payment_type,
                    material=record.material,
                    unit=record.unit,
                    barcode=record.barcode,
                    quantity=quantity_to_move,
                    price=record.price,
                    total=quantity_to_move * record.price,
                    from_Warehouse=True,
                    comment=f"Перемещено со склада {warehouse.name}"
                )
                
                # Обновляем исходную запись
                if quantity_to_move == record.quantity:
                    record.delete()
                else:
                    # Создаем запись расхода на складе
                    HistoryOdWarehouse.objects.create(
                        operation_type='outcome',
                        datetime=timezone.now(),
                        warehouse=warehouse,
                        construction_object=construction_object,
                        payment_type=record.payment_type,
                        material=record.material,
                        unit=record.unit,
                        barcode=record.barcode,
                        quantity=quantity_to_move,
                        price=record.price,
                        total=quantity_to_move * record.price,
                        comment=f"Перемещено на объект {construction_object.name}"
                    )
                    
                    # Обновляем исходную запись
                    record.quantity -= quantity_to_move
                    record.total = record.quantity * record.price
                    record.save()
                
                messages.success(request, f'Материал "{record.material}" перемещен на объект "{construction_object.name}"')
                return redirect('warehouse')
            
            except Exception as e:
                messages.error(request, f'Ошибка при перемещении: {str(e)}')
        
        # Обработка формы добавления нового материала
        else:
            form = WarehouseMaterialForm(request.POST, warehouse=warehouse)
            if form.is_valid():
                 # сохраняем основной объект и получаем его экземпляр
                # form.save()
                record = form.save()
                HistoryOdWarehouse.objects.create(
                operation_type='income',              # или 'outcome' — как вам нужно
                datetime=timezone.now(),
                warehouse=record.warehouse,
                construction_object=record.construction_object,
                payment_type=record.payment_type,
                material=record.material,
                unit=record.unit,
                barcode=record.barcode,
                quantity=record.quantity,
                price=record.price,
                total=record.quantity * record.price,
                comment=f"Добавлено на склад {record.warehouse.name}"
            )
                return redirect('warehouse')
   
    
    # Фильтрация и остальной код
    period = request.GET.get('period', 'month')
    end_date = timezone.now()
    
    if period == 'day':
        start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'week':
        start_date = (end_date - timedelta(days=end_date.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0)
    elif period == 'month':
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'quarter':
        current_quarter = (end_date.month - 1) // 3 + 1
        start_date = datetime(end_date.year, 3 * current_quarter - 2, 1)
        start_date = timezone.make_aware(start_date.replace(
            hour=0, minute=0, second=0, microsecond=0))
    else:  # custom
        start_date = request.GET.get('start_date', end_date - timedelta(days=30))
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_date = timezone.make_aware(start_date.replace(
                hour=0, minute=0, second=0, microsecond=0))
        
        end_date = request.GET.get('end_date', timezone.now())
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = timezone.make_aware(end_date.replace(
                hour=23, minute=59, second=59, microsecond=999999))
    
    # Применяем фильтрацию
    records = base_query.filter(
        datetime__gte=start_date,
        datetime__lte=end_date
        
    ).order_by('-datetime')
    
    if 'export' in request.GET:
        return generate_warehouse_excel(records, start_date, end_date)
    
    # Получаем список объектов
    objects = ConstructionObject.objects.all()
    
    # Форма для добавления материала
    form = WarehouseMaterialForm(warehouse=warehouse)
    
    records_history = HistoryOdWarehouse.objects.all()
    objects_sklada = ConstructionObjectOfWarehouse.objects.all()
        
    context = {
        
        'form': form,
        "objects_sklada":objects_sklada,
        'records_history': records_history,
        'records': records,
        'sklad_object':True,
        'warehouse': warehouse,
        'objects': objects,
        'start_date': start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else start_date,
        'end_date': end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date,
        'selected_period': period,
    }
    return render(request, 'core/warehouse.html', context)



# @login_required
# def warehouse_view(request):
#     warehouse = Warehouse.objects.first()
#     base_query = MaterialRecord.objects.filter(
#         warehouse=warehouse,
#         construction_object__isnull=True
#     ).select_related('unit', 'warehouse')
    
#     if request.method == 'POST' and 'move_to_object' in request.POST:
#         record_id = request.POST.get('record_id')
#         object_id = request.POST.get('construction_object')
#         quantity_to_move = request.POST.get('quantity')
        
#         try:
#             record = MaterialRecord.objects.get(id=record_id, warehouse=warehouse)
#             construction_object = ConstructionObject.objects.get(id=object_id)
            
#             # Преобразуем количество в Decimal
#             try:
#                 quantity_to_move = Decimal(quantity_to_move.replace(',', '.'))
#             except:
#                 quantity_to_move = Decimal(quantity_to_move)
            
#             # Проверки
#             if quantity_to_move <= 0:
#                 messages.error(request, 'Количество должно быть больше нуля')
#                 return redirect('warehouse')
                
#             if quantity_to_move > record.quantity:
#                 messages.error(request, f'Недостаточно материала (доступно: {record.quantity})')
#                 return redirect('warehouse')
            
#             # Создаем запись на объекте
#             MaterialRecord.objects.create(
#                 operation_type='income',
#                 datetime=timezone.now(),
#                 construction_object=construction_object,
#                 warehouse=None,
#                 payment_type=record.payment_type,
#                 material=record.material,
#                 unit=record.unit,
#                 barcode=record.barcode,
#                 quantity=quantity_to_move,
#                 price=record.price,
#                 total=quantity_to_move * record.price,
#                 from_Warehouse = True,
#                 comment=f"Перемещено со склада {warehouse.name}"
#             )
            
#             # Обновляем исходную запись
#             if quantity_to_move == record.quantity:
#                 record.delete()
#             else:
#                 # Создаем запись расхода на складе
#                 HistoryOdWarehouse.objects.create(
#                     operation_type='outcome',
#                     datetime=timezone.now(),
#                     warehouse=warehouse,
#                     construction_object=construction_object,
#                     payment_type=record.payment_type,
#                     material=record.material,
#                     unit=record.unit,
#                     barcode=record.barcode,
#                     quantity=quantity_to_move,
#                     price=record.price,
#                     total=quantity_to_move * record.price,
#                     comment=f"Перемещено на объект {construction_object.name}"
#                 )
                
#                 # Обновляем исходную запись
#                 record.quantity -= quantity_to_move
#                 record.total = record.quantity * record.price
#                 record.save()
#                 msg = f'Часть материала "{record.material}" ({quantity_to_move}{record.unit.short_name}) перемещена на объект "{construction_object.name}"'
            
#             messages.success(request, msg)
#             return redirect('warehouse')
              
            
#             # messages.success(request, 'Материал успешно перемещен')
#             # return redirect('warehouse')
            
#         except Exception as e:
#             messages.error(request, f'Ошибка: {str(e)}')

#         except (MaterialRecord.DoesNotExist, ConstructionObject.DoesNotExist) as e:
#             messages.error(request, 'Ошибка: не найдена запись или объект')
#         except (ValueError, InvalidOperation) as e:
#             messages.error(request, 'Ошибка: некорректное количество')
#         except Exception as e:
#             messages.error(request, f'Ошибка при перемещении: {str(e)}')
    
#     # Фильтрация и остальной код
#     period = request.GET.get('period', 'month')
#     end_date = timezone.now()
    
#     if period == 'day':
#         start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
#     elif period == 'week':
#         start_date = (end_date - timedelta(days=end_date.weekday())).replace(
#             hour=0, minute=0, second=0, microsecond=0)
#     elif period == 'month':
#         start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#     elif period == 'quarter':
#         current_quarter = (end_date.month - 1) // 3 + 1
#         start_date = datetime(end_date.year, 3 * current_quarter - 2, 1)
#         start_date = timezone.make_aware(start_date.replace(
#             hour=0, minute=0, second=0, microsecond=0))
#     else:  # custom
#         start_date = request.GET.get('start_date', end_date - timedelta(days=30))
#         if isinstance(start_date, str):
#             start_date = datetime.strptime(start_date, '%Y-%m-%d')
#             start_date = timezone.make_aware(start_date.replace(
#                 hour=0, minute=0, second=0, microsecond=0))
        
#         end_date = request.GET.get('end_date', timezone.now())
#         if isinstance(end_date, str):
#             end_date = datetime.strptime(end_date, '%Y-%m-%d')
#             end_date = timezone.make_aware(end_date.replace(
#                 hour=23, minute=59, second=59, microsecond=999999))
    
#     # Применяем фильтрацию
#     records = base_query.filter(
#         datetime__gte=start_date,
#         datetime__lte=end_date
#     ).order_by('-datetime')
    
#     # Получаем список объектов
#     objects = ConstructionObject.objects.all()
    
#      # Форма для добавления материала
#     form = WarehouseMaterialForm(warehouse=warehouse)
    
#     if request.method == 'POST':
#         form = WarehouseMaterialForm(request.POST, warehouse=warehouse)
#         if form.is_valid():
#             form.save()
#             return redirect('warehouse')
#     # Получаем список объектов для выбора
#     objects = ConstructionObject.objects.all()
#     records_history = HistoryOdWarehouse.objects.all()
#     context = {
#         'form': form,
#         'records_history':records_history,
#         'records': records,
#         'warehouse': warehouse,
#         'objects': objects,
#         'start_date': start_date.strftime('%Y-%m-%d') if isinstance(start_date, datetime) else start_date,
#         'end_date': end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime) else end_date,
#         'selected_period': period,
#     }
#     return render(request, 'core/warehouse.html', context)
def generate_warehouse_excel(queryset, start_date, end_date):
    # Создаем выходной поток в памяти
    output = BytesIO()
    
    # Создаем Excel writer с помощью xlsxwriter
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book
    
    # Подготовка данных с преобразованием дат
    data = []
    for record in queryset:
        # Преобразуем datetime с временной зоной в наивный datetime
        naive_datetime = record.datetime.replace(tzinfo=None) if record.datetime else datetime.now()
        
        data.append({
            'Дата операции': naive_datetime,
            'Материал': record.material,
            'Количество': float(record.quantity),
            'Ед. изм.': record.unit.short_name if record.unit else '-',
            'Цена за ед.': float(record.price),
            'Сумма': float(record.total),
            'Способ оплаты': record.get_payment_type_display() if hasattr(record, 'get_payment_type_display') else '-',
            'Тип операции': record.get_operation_type_display(),
            # 'Штрих-код': record.barcode or '-',
        })
    
    # Создаем DataFrame
    df = pd.DataFrame(data)
    
    # Записываем DataFrame в Excel
    df.to_excel(writer, sheet_name='Отчет по складу', index=False, startrow=4)
    
    # Получаем объекты для форматирования
    worksheet = writer.sheets['Отчет по складу']
    
    # ===== ФОРМАТИРОВАНИЕ =====
    
    # 1. Форматы ячеек
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#4472C4',  # Синий цвет фона
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    
    money_format = workbook.add_format({'num_format': '#,##0.00'})
    date_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm'})
    bold_format = workbook.add_format({'bold': True})
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'left',
        'valign': 'vcenter',
        'text_wrap': True,
    })
    
    # 2. Устанавливаем ширину столбцов
    worksheet.set_column('A:A', 18, date_format)  # Дата операции
    worksheet.set_column('B:B', 30)  # Материал
    worksheet.set_column('C:C', 12)  # Количество
    worksheet.set_column('D:D', 10)  # Ед. изм.
    worksheet.set_column('E:E', 12, money_format)  # Цена за ед.
    worksheet.set_column('F:F', 12, money_format)  # Сумма
    worksheet.set_column('G:G', 15)  # Способ оплаты
    worksheet.set_column('H:H', 15)  # Тип операции
    # worksheet.set_column('I:I', 15)  # Штрих-код
    
    # ===== ЗАГОЛОВОК ОТЧЕТА =====
    
    # 1. Основная информация
    warehouse_name = queryset.first().warehouse.name if queryset.exists() else "Склад"
    report_title = (
        f"Отчет по движению материалов на складе: {warehouse_name}\n"
        f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
        f"Дата формирования отчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        f"Всего операций: {len(df)}"
    )
    
    worksheet.merge_range('A1:I3', report_title, title_format)
    
    # 2. Заголовки столбцов
    for col_num, column_name in enumerate(df.columns.values):
        worksheet.write(4, col_num, column_name, header_format)
    
    # ===== ИТОГИ =====
    
    if not df.empty:
        last_row = len(df) + 4
        
        # Итоговая сумма
        total_sum = df['Сумма'].sum()
        
        # Формат для итогов
        total_format = workbook.add_format({
            'bold': True,
            'top': 2,
            'num_format': '#,##0.00',
        })
        
        # Статистика по операциям
        income_count = df[df['Тип операции'] == 'Приход'].shape[0]
        outcome_count = df[df['Тип операции'] == 'Расход'].shape[0]
        
        # Итоговая информация
        worksheet.write(last_row + 1, 4, 'ИТОГО:', bold_format)
        worksheet.write(last_row + 1, 5, total_sum, total_format)
        
        worksheet.write(last_row + 3, 0, f"Приходных операций: {income_count}", bold_format)
        worksheet.write(last_row + 4, 0, f"Расходных операций: {outcome_count}", bold_format)
        worksheet.write(last_row + 5, 0, f"Остаток на складе: {income_count - outcome_count} операций", bold_format)
    
    # Сохраняем Excel файл
    writer.close()
    output.seek(0)
    
    # Создаем HTTP ответ
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    
    # Формируем имя файла
    filename = (
        f"Отчет_по_складу_{warehouse_name}_"
        f"{start_date.strftime('%d.%m.%Y')}_по_{end_date.strftime('%d.%m.%Y')}.xlsx"
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from .models import MaterialRecord, ConstructionObject
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import ObjectMaterialForm
import pandas as pd
from django.http import HttpResponse

@login_required
def object_detail_view_skalda(request, object_id):
    construction_object = get_object_or_404(ConstructionObjectOfWarehouse, pk=object_id)
    
    # Базовый запрос для объекта
    base_query = StorageLocation.objects.filter(
        construction_object=construction_object,
        warehouse__isnull=True
    )
    
    # Обработка фильтрации по дате
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    if request.method == 'GET':
        period = request.GET.get('period', 'custom')
        
        if period == 'day':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = (end_date - timedelta(days=end_date.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0)
        elif period == 'month':
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'quarter':
            current_quarter = (end_date.month - 1) // 3 + 1
            start_date = datetime(end_date.year, 3 * current_quarter - 2, 1)
            start_date = timezone.make_aware(start_date.replace(
                hour=0, minute=0, second=0, microsecond=0))
        elif period == 'custom':
            custom_start = request.GET.get('start_date')
            custom_end = request.GET.get('end_date')
            
            if custom_start:
                start_date = datetime.strptime(custom_start, '%Y-%m-%d')
                start_date = timezone.make_aware(start_date.replace(
                    hour=0, minute=0, second=0, microsecond=0))
            if custom_end:
                end_date = datetime.strptime(custom_end, '%Y-%m-%d')
                end_date = timezone.make_aware(end_date.replace(
                    hour=23, minute=59, second=59, microsecond=999999))
    
    # Применяем фильтрацию по дате
    records = base_query.filter(
        datetime__gte=start_date,
        datetime__lte=end_date
    ).select_related('construction_object', 'unit').order_by('-datetime')
    
    # Экспорт в Excel
    if 'export' in request.GET:
        return generate_object_excel_report_sklad(records, construction_object, start_date, end_date)
    
    # ... остальная часть view ...
    
    # Форма для добавления материала
    form = ObjectMaterialFormSklad(construction_object=construction_object)
    
    if request.method == 'POST':
        form = ObjectMaterialFormSklad(request.POST, construction_object=construction_object)
        if form.is_valid():
            form.save()
            return redirect('object_detail_view_skalda', object_id=object_id)
    
    # Сводная информация по материалам
    materials_summary = records.values(
        'material', 'unit__short_name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sum=Sum('total')
    ).order_by('material')

    context = {
   
        'object': construction_object,
        'records': records,
        'backtoreobjectsskalda':True,
        'materials_summary': materials_summary,
        'form': form,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'selected_period': period,
    }
    return render(request, 'sklad/object_detail_sklada.html', context)

@login_required
def object_detail_view(request, object_id):
    construction_object = get_object_or_404(ConstructionObject, pk=object_id)
    
    # Базовый запрос для объекта
    base_query = MaterialRecord.objects.filter(
        construction_object=construction_object,
        warehouse__isnull=True
    )
    
    # Обработка фильтрации по дате
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    if request.method == 'GET':
        period = request.GET.get('period', 'custom')
        
        if period == 'day':
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = (end_date - timedelta(days=end_date.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0)
        elif period == 'month':
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'quarter':
            current_quarter = (end_date.month - 1) // 3 + 1
            start_date = datetime(end_date.year, 3 * current_quarter - 2, 1)
            start_date = timezone.make_aware(start_date.replace(
                hour=0, minute=0, second=0, microsecond=0))
        elif period == 'custom':
            custom_start = request.GET.get('start_date')
            custom_end = request.GET.get('end_date')
            
            if custom_start:
                start_date = datetime.strptime(custom_start, '%Y-%m-%d')
                start_date = timezone.make_aware(start_date.replace(
                    hour=0, minute=0, second=0, microsecond=0))
            if custom_end:
                end_date = datetime.strptime(custom_end, '%Y-%m-%d')
                end_date = timezone.make_aware(end_date.replace(
                    hour=23, minute=59, second=59, microsecond=999999))
    
    # Применяем фильтрацию по дате
    records = base_query.filter(
        datetime__gte=start_date,
        datetime__lte=end_date
    ).select_related('construction_object', 'unit').order_by('-datetime')
    
    # Экспорт в Excel
    if 'export' in request.GET:
        return generate_object_excel_report(records, construction_object, start_date, end_date)
    
    # ... остальная часть view ...
    
    # Форма для добавления материала
    form = ObjectMaterialForm(construction_object=construction_object)
    
    if request.method == 'POST':
        form = ObjectMaterialForm(request.POST, construction_object=construction_object)
        if form.is_valid():
            form.save()
            return redirect('object_detail', object_id=object_id)
    
    # Сводная информация по материалам
    materials_summary = records.values(
        'material', 'unit__short_name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sum=Sum('total')
    ).order_by('material')
    
    context = {
        'object': construction_object,
        'records': records,
        'back':True,
        'materials_summary': materials_summary,
        'form': form,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'selected_period': period,
    }
    return render(request, 'core/object_detail.html', context)
def generate_object_excel(queryset, construction_object, start_date, end_date):
    # Создаем DataFrame
    data = []
    for record in queryset:
        data.append({
            'Дата': record.datetime.strftime('%d.%m.%Y %H:%M'),
            'Материал': record.material,
            'Количество': float(record.quantity),
            'Ед. изм.': record.unit.short_name,
            'Цена': float(record.price),
            'Сумма': float(record.total),
            'Тип операции': record.payment_type or '-',
            # 'Штрих-код': record.barcode or '-',
            'Тип операции': record.get_operation_type_display(),
        })
    
    df = pd.DataFrame(data)
    
    # Создаем Excel файл с помощью XlsxWriter
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Материалы', index=False)
    
    # Получаем объекты xlsxwriter
    workbook = writer.book
    worksheet = writer.sheets['Материалы']
    
    # Форматы
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#4472C4',
        'font_color': 'white',
        'border': 1,
    })
    
    money_format = workbook.add_format({'num_format': '#,##0.00'})
    date_format = workbook.add_format({'num_format': 'dd.mm.yyyy hh:mm'})
    
    # Ширина колонок
    worksheet.set_column('A:A', 18)  # Дата
    worksheet.set_column('B:B', 30)  # Материал
    worksheet.set_column('C:C', 12)  # Количество
    worksheet.set_column('D:D', 8)   # Ед. изм.
    worksheet.set_column('E:E', 12, money_format)  # Цена
    worksheet.set_column('F:F', 12, money_format)  # Сумма
    worksheet.set_column('G:G', 15)  # Штрих-код
    worksheet.set_column('H:H', 12)  # Тип операции
    
    # Заголовки
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # Добавляем информацию об объекте
    info_text = f"Отчет по объекту: {construction_object.name}\n" \
                f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n" \
                f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    worksheet.merge_range('A1:H3', info_text, workbook.add_format({
        'bold': True,
        'align': 'left',
        'valign': 'vcenter',
        'font_size': 12,
    }))
    
    # Сдвигаем таблицу вниз на 3 строки
    df.to_excel(writer, sheet_name='Материалы', startrow=3, index=False)
    
    # Итоговая строка
    if not df.empty:
        last_row = len(df) + 3
        worksheet.write(last_row, 5, df['Сумма'].sum(), workbook.add_format({
            'num_format': '#,##0.00',
            'bold': True,
            'top': 1,
        }))
        worksheet.write(last_row, 4, 'ИТОГО:', workbook.add_format({
            'bold': True,
            'align': 'right',
            'top': 1,
        }))
    
    writer.close()
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Отчет_по_объекту_{construction_object.name}_{start_date.date()}_по_{end_date.date()}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response