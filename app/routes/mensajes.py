from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Contacto, Mensaje, Categoria
from app.services.twilio_service import TwilioService
from app.routes import mensajes_bp

twilio_service = TwilioService()

@mensajes_bp.route('/')
@login_required
def historial():
    pagina = request.args.get('page', 1, type=int)
    mensajes = Mensaje.query.filter_by(usuario_id=current_user.id).order_by(
        Mensaje.fecha_envio.desc()
    ).paginate(page=pagina, per_page=20)
    
    return render_template('mensajes/historial.html', mensajes=mensajes)

@mensajes_bp.route('/enviar', methods=['GET', 'POST'])
@login_required
def enviar():
    if request.method == 'POST':
        try:
            contenido = request.form.get('contenido')
            tipo_destinatario = request.form.get('tipo_destinatario')
            
            if not contenido or len(contenido) == 0:
                flash('El mensaje no puede estar vacío', 'error')
                return redirect(url_for('mensajes.enviar'))
            
            # Obtener contactos según el tipo
            if tipo_destinatario == 'todos':
                contactos = Contacto.query.filter_by(
                    usuario_id=current_user.id,
                    activo=True
                ).all()
            elif tipo_destinatario == 'categoria':
                categoria_id = request.form.get('categoria_id')
                contactos = Contacto.query.filter_by(
                    usuario_id=current_user.id,
                    categoria_id=categoria_id,
                    activo=True
                ).all()
            elif tipo_destinatario == 'individual':
                contacto_id = request.form.get('contacto_id')
                contacto = Contacto.query.get_or_404(contacto_id)
                if contacto.usuario_id != current_user.id:
                    flash('No tienes permiso', 'error')
                    return redirect(url_for('mensajes.enviar'))
                contactos = [contacto]
            
            if not contactos:
                flash('No hay contactos para enviar', 'error')
                return redirect(url_for('mensajes.enviar'))
            
            # Enviar mensajes
            resultados = twilio_service.enviar_mensajes_masivos(
                contactos,
                contenido,
                current_user.id
            )
            
            exitosos = sum(1 for r in resultados if r['exito'])
            flash(f'Mensajes enviados: {exitosos}/{len(resultados)}', 'success')
            return redirect(url_for('mensajes.historial'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('mensajes.enviar'))
    
    categorias = Categoria.query.filter_by(usuario_id=current_user.id).all()
    contactos = Contacto.query.filter_by(usuario_id=current_user.id).all()
    
    return render_template('mensajes/enviar.html', categorias=categorias, contactos=contactos)

@mensajes_bp.route('/api/estado/<mensaje_id>')
@login_required
def api_estado(mensaje_id):
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    
    if mensaje.usuario_id != current_user.id:
        return jsonify({'exito': False, 'error': 'No autorizado'}), 403
    
    if mensaje.sid_twilio:
        estado = twilio_service.obtener_estado_mensaje(mensaje.sid_twilio)
        return jsonify(estado)
    
    return jsonify({'estado': mensaje.estado})
