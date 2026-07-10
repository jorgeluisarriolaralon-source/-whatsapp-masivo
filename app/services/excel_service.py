import openpyxl
from app.models import Contacto, Categoria, CargaExcel
from app import db
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class ExcelService:
    """Servicio para cargar contactos desde Excel"""
    
    @staticmethod
    def cargar_contactos(archivo, usuario_id, categoria_id=None):
        """Carga contactos desde un archivo Excel"""
        try:
            wb = openpyxl.load_workbook(archivo)
            ws = wb.active
            
            contactos_nuevos = 0
            contactos_duplicados = 0
            contactos_error = 0
            errores = []
            
            # Saltar encabezado (primera fila)
            for fila, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    # Esperamos: nombre, telefono, email (opcional), categoria (opcional)
                    nombre = row[0]
                    telefono = row[1]
                    email = row[2] if len(row) > 2 else None
                    cat_nombre = row[3] if len(row) > 3 else None
                    
                    # Validaciones
                    if not nombre or not telefono:
                        errores.append(f'Fila {fila}: Nombre o teléfono vacío')
                        contactos_error += 1
                        continue
                    
                    # Verificar si el contacto ya existe
                    existe = Contacto.query.filter_by(
                        telefono=str(telefono),
                        usuario_id=usuario_id
                    ).first()
                    
                    if existe:
                        contactos_duplicados += 1
                        continue
                    
                    # Obtener o crear categoría
                    cat_id = categoria_id
                    if cat_nombre:
                        categoria = Categoria.query.filter_by(
                            nombre=cat_nombre,
                            usuario_id=usuario_id
                        ).first()
                        if not categoria:
                            categoria = Categoria(
                                nombre=cat_nombre,
                                usuario_id=usuario_id
                            )
                            db.session.add(categoria)
                            db.session.flush()
                        cat_id = categoria.id
                    
                    # Crear nuevo contacto
                    nuevo_contacto = Contacto(
                        nombre=str(nombre),
                        telefono=str(telefono),
                        email=str(email) if email else None,
                        usuario_id=usuario_id,
                        categoria_id=cat_id
                    )
                    db.session.add(nuevo_contacto)
                    contactos_nuevos += 1
                
                except Exception as e:
                    logger.error(f'Error en fila {fila}: {str(e)}')
                    errores.append(f'Fila {fila}: {str(e)}')
                    contactos_error += 1
            
            # Guardar cambios
            db.session.commit()
            
            # Registrar carga
            carga = CargaExcel(
                usuario_id=usuario_id,
                nombre_archivo=archivo.filename if hasattr(archivo, 'filename') else 'carga',
                cantidad_contactos=contactos_nuevos + contactos_duplicados + contactos_error,
                cantidad_exitosos=contactos_nuevos,
                cantidad_errores=contactos_error,
                estado='exitoso'
            )
            db.session.add(carga)
            db.session.commit()
            
            return {
                'exito': True,
                'nuevos': contactos_nuevos,
                'duplicados': contactos_duplicados,
                'errores': contactos_error,
                'detalle_errores': errores
            }
        
        except Exception as e:
            logger.error(f'Error al cargar Excel: {str(e)}')
            db.session.rollback()
            return {
                'exito': False,
                'error': str(e)
            }
