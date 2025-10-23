"""
Utilidad para importar productos y materias primas desde archivo CSV/Excel
"""
import csv
import traceback
from decimal import Decimal
from config.database import get_session, close_session
from models import Product, RawMaterial, ProductMaterial, Category

class ProductImporter:
    """Clase para importar productos y sus materias primas desde CSV"""
    
    # Mapeo de columnas del CSV a materias primas
    MATERIAL_COLUMNS = {
        'ACEITE (ML)': 'Aceite',
        'MAIZ     (GR)': 'Maíz',
        'SAL       (GR)': 'Sal',
        'CARAMELO (GR)': 'Caramelo',
        'QUESO   (GR)': 'Queso',
        'LIMON       (GR)': 'Limón',
        'TOCINETA   (GR)': 'Tocineta',
        'COLORES    (GR)': 'Colores',
        'BOLSA NORMAL (UND)': 'Bolsa Normal',
        'BOLSA AL MAYOR (UND)': 'Bolsa al Mayor',
        'CAJA POPETA (UND)': 'Caja Popeta',
        'JUGUETE       (UND)': 'Juguete',
        'GRANIZADO   (ONZ)': 'Granizado',
        'VASOS    (UND)': 'Vasos',
        'PITILLOS    (UND)': 'Pitillos',
        'PERLAS    (GR)': 'Perlas',
        'TOPIN GOMAS': 'Topin Gomas',
        'GASEOSA     (UND)': 'Gaseosa',
        'AGUA           (UND)': 'Agua',
        'AZUCAR    (GR)': 'Azúcar',
        'VASO ALGODÓN': 'Vaso Algodón',
        'PICANTE (GR)': 'Picante'
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.created_products = 0
        self.updated_products = 0
        self.created_materials = 0
        self.created_relations = 0
    
    def parse_csv_value(self, value):
        """
        Parsea un valor del CSV que puede estar en formato "123,45" o "123.45"
        Los valores negativos indican consumo (se toman como positivos)
        """
        if not value or value.strip() == '' or value.strip() == '0':
            return 0.0
        
        try:
            # Limpiar el valor
            value = str(value).strip()
            
            # Si es 0 o vacío, retornar 0
            if value in ['0', '0,0', '0.0', '']:
                return 0.0
            
            # Reemplazar coma por punto para formato decimal
            value = value.replace(',', '.')
            # Tomar valor absoluto (los negativos indican consumo)
            parsed_value = abs(float(value))
            
            # Solo retornar si es mayor que 0
            return parsed_value if parsed_value > 0 else 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_price(self, price_str):
        """Parsea un precio en formato "$ 5.000" o similar"""
        if not price_str or price_str.strip() == '':
            return 0.0
        
        try:
            # Limpiar el precio
            price_str = str(price_str).strip()
            
            # Si es 0, retornar 0
            if price_str in ['0', '$ 0', '0,0', '0.0']:
                return 0.0
            
            # Remover símbolo de pesos y espacios
            clean_price = price_str.replace('$', '').replace(' ', '').strip()
            
            # Si tiene punto como separador de miles (formato colombiano)
            if ',' in clean_price and '.' in clean_price:
                # Formato: 5.000,50 -> 5000.50
                parts = clean_price.split(',')
                if len(parts) == 2:
                    integer_part = parts[0].replace('.', '')  # Quitar puntos de miles
                    decimal_part = parts[1]
                    clean_price = f"{integer_part}.{decimal_part}"
            elif ',' in clean_price and '.' not in clean_price:
                # Formato: 5.000 -> 5000
                clean_price = clean_price.replace('.', '')
            elif ',' in clean_price:
                # Formato: 5000,50 -> 5000.50
                clean_price = clean_price.replace(',', '.')
            elif '.' in clean_price and ',' not in clean_price:
                # Formato: 5.000 -> 5000 (solo puntos de miles)
                clean_price = clean_price.replace('.', '')
            
            return float(clean_price)
        except (ValueError, AttributeError) as e:
            self.warnings.append(f"Error parseando precio '{price_str}': {str(e)}")
            return 0.0
    
    def get_or_create_material(self, session, material_name, unit):
        """Obtiene o crea una materia prima"""
        try:
            # Buscar materia prima existente
            material = session.query(RawMaterial).filter_by(name=material_name).first()
            
            if not material:
                # Crear nueva materia prima
                material = RawMaterial(
                    name=material_name,
                    sku=f"MAT-{material_name[:10].upper()}",
                    unit=unit,
                    stock=0,
                    min_stock=10,
                    cost_per_unit=0
                )
                session.add(material)
                session.flush()
                self.created_materials += 1
                self.warnings.append(f"Materia prima creada: {material_name} ({unit})")
            
            return material
        except Exception as e:
            self.warnings.append(f"Error creando materia prima {material_name}: {str(e)}")
            raise e
    
    def get_unit_from_column(self, column_name):
        """Extrae la unidad de medida del nombre de columna"""
        if '(ML)' in column_name:
            return 'ml'
        elif '(GR)' in column_name:
            return 'g'
        elif '(ONZ)' in column_name:
            return 'oz'
        elif '(UND)' in column_name:
            return 'und'
        else:
            return 'und'
    
    def get_or_create_category(self, session, category_name):
        """Obtiene o crea una categoría"""
        try:
            category = session.query(Category).filter_by(name=category_name).first()
            
            if not category:
                category = Category(
                    name=category_name,
                    description=f"Categoría {category_name}"
                )
                session.add(category)
                session.flush()
                self.warnings.append(f"Categoría creada: {category_name}")
            
            return category
        except Exception as e:
            self.warnings.append(f"Error creando categoría {category_name}: {str(e)}")
            raise e
    
    def import_from_csv(self, file_path, default_stock=100, update_existing=False):
        """
        Importa productos desde un archivo CSV
        
        Args:
            file_path: Ruta al archivo CSV
            default_stock: Stock inicial para productos nuevos
            update_existing: Si True, actualiza productos existentes
        
        Returns:
            dict con estadísticas de la importación
        """
        session = get_session()
        
        try:
            # Verificar conexión a la base de datos
            try:
                from sqlalchemy import text
                session.execute(text("SELECT 1"))
            except Exception as db_error:
                self.errors.append(f"Error de conexión a la base de datos: {str(db_error)}")
                return {
                    'success': False,
                    'error': f"Error de conexión a la base de datos: {str(db_error)}",
                    'errors': self.errors,
                    'warnings': self.warnings
                }
            with open(file_path, 'r', encoding='utf-8') as file:
                # Leer todas las líneas y encontrar la línea de encabezados
                lines = file.readlines()
                
                # Buscar la línea que contiene "CODIGO" (línea de encabezados)
                header_line_idx = None
                for i, line in enumerate(lines):
                    if 'CODIGO' in line and 'PRODUCTO' in line:
                        header_line_idx = i
                        break
                
                if header_line_idx is None:
                    raise Exception("No se encontró la línea de encabezados con 'CODIGO' y 'PRODUCTO'")
                
                # Crear un nuevo archivo temporal sin las líneas vacías
                import tempfile
                import os
                
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8', newline='')
                
                # Escribir la línea de encabezados
                temp_file.write(lines[header_line_idx])
                
                # Escribir las líneas de datos (después de la línea de encabezados)
                for line in lines[header_line_idx + 1:]:
                    temp_file.write(line)
                
                temp_file.close()
                
                # Leer el archivo temporal
                with open(temp_file.name, 'r', encoding='utf-8') as temp_file_handle:
                    csv_reader = csv.DictReader(temp_file_handle)
                    
                    for row_idx, row in enumerate(csv_reader, start=2):
                        product_name = "Desconocido"  # Valor por defecto
                        try:
                            # Saltar la primera fila de ejemplo (código 0)
                            codigo = row.get('CODIGO', '').strip()
                            if not codigo or codigo == '0':
                                continue
                            
                            
                            # Extraer datos del producto
                            product_name = row.get('PRODUCTO', '').strip()
                            if not product_name:
                                self.warnings.append(f"Fila {row_idx}: Nombre de producto vacío")
                                continue
                            
                            # Parsear precio
                            price_str = row.get('VALOR UNITARIO', '0')
                            sale_price = self.parse_price(price_str)
                            
                            # Generar SKU
                            sku = f"PROD-{codigo.zfill(3)}"
                            
                            # Buscar producto existente
                            product = session.query(Product).filter_by(sku=sku).first()
                            
                            if product:
                                if update_existing:
                                    # Actualizar producto existente
                                    product.name = product_name
                                    product.sale_price = sale_price
                                    self.updated_products += 1
                                    self.warnings.append(f"Producto actualizado: {product_name}")
                                else:
                                    self.warnings.append(f"Producto ya existe (omitido): {product_name}")
                                    continue
                            else:
                                # Determinar categoría basada en el nombre
                                if 'SENA' in product_name.upper():
                                    category_name = 'SENA'
                                elif 'COLEGIO' in product_name.upper():
                                    category_name = 'COLEGIO'
                                elif 'MAYOR' in product_name.upper():
                                    category_name = 'AL MAYOR'
                                elif 'GRANIZADO' in product_name.upper():
                                    category_name = 'GRANIZADOS'
                                elif 'ALGODÓN' in product_name.upper():
                                    category_name = 'ALGODÓN'
                                elif 'COCA' in product_name.upper() or 'AGUA' in product_name.upper():
                                    category_name = 'BEBIDAS'
                                else:
                                    category_name = 'CRISPETAS'
                                
                                category = self.get_or_create_category(session, category_name)
                                
                            # Crear nuevo producto
                            product = Product(
                                sku=sku,
                                name=product_name,
                                description=f"Producto importado: {product_name}",
                                category_id=category.id,
                                stock=default_stock,
                                min_stock=10,
                                cost_price=sale_price * 0.4,  # Estimar costo como 40% del precio
                                sale_price=sale_price
                            )
                            session.add(product)
                            session.flush()
                            self.created_products += 1
                            
                            # Procesar materias primas
                            materials_processed = 0
                            for column_name, material_name in self.MATERIAL_COLUMNS.items():
                                quantity_str = row.get(column_name, '0')
                                quantity = self.parse_csv_value(quantity_str)
                                
                                if quantity > 0:
                                    materials_processed += 1
                                    # Obtener unidad de medida
                                    unit = self.get_unit_from_column(column_name)
                                    
                                    # Obtener o crear materia prima
                                    material = self.get_or_create_material(session, material_name, unit)
                                    
                                    # Verificar si ya existe la relación
                                    existing_relation = session.query(ProductMaterial).filter_by(
                                        product_id=product.id,
                                        raw_material_id=material.id
                                    ).first()
                                    
                                    if existing_relation:
                                        # Actualizar cantidad
                                        existing_relation.quantity_needed = quantity
                                    else:
                                        # Crear relación producto-materia prima
                                        product_material = ProductMaterial(
                                            product_id=product.id,
                                            raw_material_id=material.id,
                                            quantity_needed=quantity
                                        )
                                        session.add(product_material)
                                        self.created_relations += 1
                            
                            if materials_processed == 0:
                                self.warnings.append(f"DEBUG: {product_name} - Sin materias primas procesadas")
                            else:
                                self.warnings.append(f"DEBUG: {product_name} - {materials_processed} materias primas procesadas")
                            
                        except Exception as e:
                            error_msg = f"Fila {row_idx} ({product_name}): {str(e)}"
                            self.errors.append(error_msg)
                            continue
                
                # Confirmar cambios
                try:
                    session.commit()
                except Exception as commit_error:
                    session.rollback()
                    self.errors.append(f"Error al confirmar cambios: {str(commit_error)}")
                    raise commit_error
                
                # Limpiar archivo temporal
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                
                # Agregar estadísticas finales
                self.warnings.append(f"DEBUG: Estadísticas finales - Productos: {self.created_products}, Materias: {self.created_materials}, Relaciones: {self.created_relations}")
                
                return {
                    'success': True,
                    'created_products': self.created_products,
                    'updated_products': self.updated_products,
                    'created_materials': self.created_materials,
                    'created_relations': self.created_relations,
                    'errors': self.errors,
                    'warnings': self.warnings
                }
                
        except Exception as e:
            session.rollback()
            self.errors.append(f"Error general: {str(e)}\n{traceback.format_exc()}")
            
            # Limpiar archivo temporal en caso de error
            try:
                if 'temp_file' in locals():
                    os.unlink(temp_file.name)
            except:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'errors': self.errors,
                'warnings': self.warnings
            }
        finally:
            close_session()
    
    def import_from_excel(self, file_path, default_stock=100, update_existing=False):
        """
        Importa productos desde un archivo Excel
        Convierte el Excel a CSV temporalmente y luego importa
        """
        try:
            import openpyxl
            import tempfile
            import os
            
            # Cargar el archivo Excel
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            # Crear archivo CSV temporal
            temp_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8', newline='')
            csv_writer = csv.writer(temp_csv)
            
            # Escribir datos al CSV
            for row in ws.iter_rows(values_only=True):
                csv_writer.writerow(row)
            
            temp_csv.close()
            
            # Importar desde el CSV temporal
            result = self.import_from_csv(temp_csv.name, default_stock, update_existing)
            
            # Eliminar archivo temporal
            os.unlink(temp_csv.name)
            
            return result
            
        except ImportError:
            return {
                'success': False,
                'error': 'La librería openpyxl no está instalada. Use un archivo CSV o instale openpyxl.',
                'errors': ['openpyxl no disponible'],
                'warnings': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'errors': [f"Error al procesar Excel: {str(e)}\n{traceback.format_exc()}"],
                'warnings': []
            }
