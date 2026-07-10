from app import db
from app.models import Mensaje
from twilio.rest import Client
import os
import logging

logger = logging.getLogger(__name__)

class TwilioService:
    """Servicio para integración con Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_number]):
            raise ValueError('Credenciales de Twilio no configuradas')
        
        self.client = Client(self.account_sid, self.auth_token)
    
    def enviar_mensaje(self, numero_destino, contenido, usuario_id, contacto_id):
        """Envía un mensaje WhatsApp"""
        try:
            # Asegurar que el número tenga formato +
            if not numero_destino.startswith('+'):
                numero_destino = '+' + numero_destino
            
            # Enviar mensaje
            message = self.client.messages.create(
                from_=f'whatsapp:{self.whatsapp_number}',
                body=contenido,
                to=f'whatsapp:{numero_destino}'
            )
            
            # Registrar en base de datos
            registro = Mensaje(
                usuario_id=usuario_id,
                contacto_id=contacto_id,
                contenido=contenido,
                estado='enviado',
                sid_twilio=message.sid
            )
            db.session.add(registro)
            db.session.commit()
            
            logger.info(f'Mensaje enviado a {numero_destino} - SID: {message.sid}')
            return {'exito': True, 'sid': message.sid}
        
        except Exception as e:
            logger.error(f'Error al enviar mensaje a {numero_destino}: {str(e)}')
            
            # Registrar error en BD
            registro = Mensaje(
                usuario_id=usuario_id,
                contacto_id=contacto_id,
                contenido=contenido,
                estado='error',
                error_mensaje=str(e)
            )
            db.session.add(registro)
            db.session.commit()
            
            return {'exito': False, 'error': str(e)}
    
    def enviar_mensajes_masivos(self, contactos, contenido, usuario_id):
        """Envía mensajes a múltiples contactos"""
        resultados = []
        
        for contacto in contactos:
            resultado = self.enviar_mensaje(
                contacto.telefono,
                contenido,
                usuario_id,
                contacto.id
            )
            resultados.append({
                'contacto_id': contacto.id,
                'nombre': contacto.nombre,
                'telefono': contacto.telefono,
                **resultado
            })
        
        return resultados
    
    def obtener_estado_mensaje(self, sid):
        """Obtiene el estado de un mensaje enviado"""
        try:
            message = self.client.messages(sid).fetch()
            return {
                'sid': message.sid,
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
        except Exception as e:
            logger.error(f'Error al obtener estado: {str(e)}')
            return None
