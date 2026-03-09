from django.contrib import admin
from .models import (
    BitacoraPrincipalIndicadorBase,
    BitacoraPrincipalIndicadorOg,
    BitacoraPrincipalIndicadorOE,
    BitacoraPrincipalIndicadorRog,
    BitacoraPrincipalIndicadorRoe,
)


# ============================================
# ADMIN BASE (solo para herencia, no registrado)
# ============================================
class BitacoraPrincipalBaseAdmin(admin.ModelAdmin):
    """
    Admin base con campos comunes
    """
    list_display = [
        'id',
        'tipo_indicador',
        'tipo_dato',
        'fecha_registro',
        'usuario_registro',
        'timestamp_registro',
    ]
    
    list_filter = ['tipo_indicador', 'tipo_dato', 'fecha_registro']
    
    search_fields = ['id', 'observaciones', 'valor_literal']
    
    # ✅ CAMPOS NO EDITABLES (porque son auto_now o auto_now_add)
    readonly_fields = [
        'timestamp_registro',
        'timestamp_ultima_modificacion',
    ]
    
    # ✅ TODOS los demás campos editables
    fieldsets = [
        ('📋 INFORMACIÓN BÁSICA', {
            'fields': [
                ('tipo_indicador', 'tipo_dato'),
                'fecha_registro',
                'usuario_registro',
            ]
        }),
        ('📊 VALORES', {
            'fields': [
                'valor_literal',
                ('valor_numerico', 'valor_porcentual'),
            ]
        }),
        ('📝 OBSERVACIONES', {
            'fields': ['observaciones'],
        }),
        ('📎 ARCHIVOS Y SNAPSHOT', {
            'fields': ['archivos_adjuntos', 'snapshot_indicador'],
            'classes': ['wide'],
        }),
        ('⏱️ TIMESTAMPS (Solo lectura)', {
            'fields': [
                ('timestamp_registro', 'timestamp_ultima_modificacion'),
            ],
            'classes': ['collapse'],  # Opcional: colapsable para no ocupar espacio
        }),
    ]


# ============================================
# ADMIN ESPECÍFICOS - TODOS EDITABLES
# ============================================

@admin.register(BitacoraPrincipalIndicadorOg)
class BitacoraPrincipalIndicadorOgAdmin(BitacoraPrincipalBaseAdmin):
    """
    Admin para Bitácora Principal OG - COMPLETAMENTE EDITABLE
    """
    list_display = BitacoraPrincipalBaseAdmin.list_display + [
        'indicador_og',
        'informe_actividad',
        'informe_tarea',
    ]
    
    list_filter = BitacoraPrincipalBaseAdmin.list_filter + ['informe_actividad', 'informe_tarea']
    
    # Agregar raw_id_fields para mejor rendimiento con ForeignKeys
    raw_id_fields = ['indicador_og', 'informe_actividad', 'informe_tarea']
    
    fieldsets = BitacoraPrincipalBaseAdmin.fieldsets + [
        ('🔗 RELACIONES ESPECÍFICAS (OG)', {
            'fields': [
                'indicador_og',
                ('informe_actividad', 'informe_tarea'),
            ]
        }),
    ]


@admin.register(BitacoraPrincipalIndicadorOE)
class BitacoraPrincipalIndicadorOEAdmin(BitacoraPrincipalBaseAdmin):
    """
    Admin para Bitácora Principal OE - COMPLETAMENTE EDITABLE
    """
    list_display = BitacoraPrincipalBaseAdmin.list_display + [
        'indicador_oe',
        'informe_actividad',
        'informe_tarea',
    ]
    
    list_filter = BitacoraPrincipalBaseAdmin.list_filter + ['informe_actividad', 'informe_tarea']
    
    raw_id_fields = ['indicador_oe', 'informe_actividad', 'informe_tarea']
    
    fieldsets = BitacoraPrincipalBaseAdmin.fieldsets + [
        ('🔗 RELACIONES ESPECÍFICAS (OE)', {
            'fields': [
                'indicador_oe',
                ('informe_actividad', 'informe_tarea'),
            ]
        }),
    ]


@admin.register(BitacoraPrincipalIndicadorRog)
class BitacoraPrincipalIndicadorRogAdmin(BitacoraPrincipalBaseAdmin):
    """
    Admin para Bitácora Principal ROG - COMPLETAMENTE EDITABLE
    """
    list_display = BitacoraPrincipalBaseAdmin.list_display + [
        'indicador_rog',
        'informe_actividad',
        'informe_tarea',
    ]
    
    list_filter = BitacoraPrincipalBaseAdmin.list_filter + ['informe_actividad', 'informe_tarea']
    
    raw_id_fields = ['indicador_rog', 'informe_actividad', 'informe_tarea']
    
    fieldsets = BitacoraPrincipalBaseAdmin.fieldsets + [
        ('🔗 RELACIONES ESPECÍFICAS (ROG)', {
            'fields': [
                'indicador_rog',
                ('informe_actividad', 'informe_tarea'),
            ]
        }),
    ]


@admin.register(BitacoraPrincipalIndicadorRoe)
class BitacoraPrincipalIndicadorRoeAdmin(BitacoraPrincipalBaseAdmin):
    """
    Admin para Bitácora Principal ROE - COMPLETAMENTE EDITABLE
    """
    list_display = BitacoraPrincipalBaseAdmin.list_display + [
        'indicador_roe',
        'informe_actividad',
        'informe_tarea',
    ]
    
    list_filter = BitacoraPrincipalBaseAdmin.list_filter + ['informe_actividad', 'informe_tarea']
    
    raw_id_fields = ['indicador_roe', 'informe_actividad', 'informe_tarea']
    
    fieldsets = BitacoraPrincipalBaseAdmin.fieldsets + [
        ('🔗 RELACIONES ESPECÍFICAS (ROE)', {
            'fields': [
                'indicador_roe',
                ('informe_actividad', 'informe_tarea'),
            ]
        }),
    ]


# ============================================
# ADMIN PARA EL MODELO BASE (Polymorphic)
# ============================================
@admin.register(BitacoraPrincipalIndicadorBase)
class BitacoraPrincipalIndicadorBaseAdmin(admin.ModelAdmin):
    """
    Admin para el modelo base (Polymorphic) - SÓLO VISUALIZACIÓN
    """
    list_display = ['id', 'tipo_indicador', 'tipo_dato', 'fecha_registro']
    list_filter = ['tipo_indicador', 'tipo_dato']
    
    # Solo lectura porque es polimórfico
    readonly_fields = [field.name for field in BitacoraPrincipalIndicadorBase._meta.fields]
    
    def has_add_permission(self, request):
        return False  # No permitir crear desde el base
    
    def has_delete_permission(self, request, obj=None):
        return False  # No permitir eliminar desde el base