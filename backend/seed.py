"""
Database seeding script for DocuDash
Run with: python seed.py
"""
from datetime import datetime
from app.database import SessionLocal, engine, Base
from app.models import (
    User, UserRole, UserStatus,
    Group, GroupSubscription,
    Application, ApplicationStatus,
    Feature, FeatureStatus,
    TestCase, TestCaseType, TestCasePriority, TestCaseStatus,
    GherkinStep, GherkinStepType, GherkinSubStep,
    GitlabPipeline, PipelineStatus,
    TestCasePipelineResult, TestCaseResultStatus,
    TestRequest, TestRequestStatus
)
from app.services.auth_service import hash_password

# Create tables
Base.metadata.create_all(bind=engine)


def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database...")
        
        # Create admin user
        admin_password = hash_password("admin123")
        admin = db.query(User).filter(User.email == "admin@docudash.com").first()
        if not admin:
            admin = User(
                email="admin@docudash.com",
                password=admin_password,
                first_name="Admin",
                last_name="DocuDash",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        print(f"✅ Admin user created: {admin.email}")
        
        # Create test user
        user_password = hash_password("user123")
        user = db.query(User).filter(User.email == "usuario@docudash.com").first()
        if not user:
            user = User(
                email="usuario@docudash.com",
                password=user_password,
                first_name="Usuario",
                last_name="Prueba",
                role=UserRole.USER,
                status=UserStatus.ACTIVE
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        print(f"✅ Test user created: {user.email}")
        
        # Create groups
        group_salud = db.query(Group).filter(Group.name == "Portal de Salud").first()
        if not group_salud:
            group_salud = Group(
                name="Portal de Salud",
                description="Aplicaciones del portal de salud y prestaciones médicas"
            )
            db.add(group_salud)
            db.commit()
            db.refresh(group_salud)
        
        group_admin = db.query(Group).filter(Group.name == "Sistemas Administrativos").first()
        if not group_admin:
            group_admin = Group(
                name="Sistemas Administrativos",
                description="Aplicaciones de gestión interna y administrativa"
            )
            db.add(group_admin)
            db.commit()
            db.refresh(group_admin)
        
        group_mobile = db.query(Group).filter(Group.name == "Aplicaciones Mobile").first()
        if not group_mobile:
            group_mobile = Group(
                name="Aplicaciones Mobile",
                description="Aplicaciones móviles para socios y prestadores"
            )
            db.add(group_mobile)
            db.commit()
            db.refresh(group_mobile)
        
        print("✅ Groups created")
        
        # Create applications
        app_autorizaciones = db.query(Application).filter(
            Application.name == "Autorizaciones Online",
            Application.group_id == group_salud.id
        ).first()
        if not app_autorizaciones:
            app_autorizaciones = Application(
                name="Autorizaciones Online",
                description="Sistema de autorizaciones de prestaciones médicas",
                status=ApplicationStatus.ACTIVE,
                group_id=group_salud.id,
                gitlab_project_id="12345",
                gitlab_project_url="https://gitlab.com/empresa/autorizaciones"
            )
            db.add(app_autorizaciones)
            db.commit()
            db.refresh(app_autorizaciones)
        
        app_credenciales = db.query(Application).filter(
            Application.name == "Credencial Digital",
            Application.group_id == group_salud.id
        ).first()
        if not app_credenciales:
            app_credenciales = Application(
                name="Credencial Digital",
                description="Gestión de credenciales digitales de socios",
                status=ApplicationStatus.ACTIVE,
                group_id=group_salud.id
            )
            db.add(app_credenciales)
            db.commit()
            db.refresh(app_credenciales)
        
        app_facturacion = db.query(Application).filter(
            Application.name == "Facturación",
            Application.group_id == group_admin.id
        ).first()
        if not app_facturacion:
            app_facturacion = Application(
                name="Facturación",
                description="Sistema de facturación y cobranzas",
                status=ApplicationStatus.ACTIVE,
                group_id=group_admin.id
            )
            db.add(app_facturacion)
            db.commit()
            db.refresh(app_facturacion)
        
        print("✅ Applications created")
        
        # Create features
        feature_login = db.query(Feature).filter(
            Feature.name == "Login y Autenticación",
            Feature.application_id == app_autorizaciones.id
        ).first()
        if not feature_login:
            feature_login = Feature(
                name="Login y Autenticación",
                description="Funcionalidad de ingreso al sistema con validación de credenciales",
                status=FeatureStatus.PRODUCTIVE,
                application_id=app_autorizaciones.id,
                feature_file_path="features/login.feature"
            )
            db.add(feature_login)
            db.commit()
            db.refresh(feature_login)
        
        feature_solicitud = db.query(Feature).filter(
            Feature.name == "Solicitud de Autorización",
            Feature.application_id == app_autorizaciones.id
        ).first()
        if not feature_solicitud:
            feature_solicitud = Feature(
                name="Solicitud de Autorización",
                description="Proceso de solicitud de autorización de prestaciones",
                status=FeatureStatus.PRODUCTIVE,
                application_id=app_autorizaciones.id,
                feature_file_path="features/solicitud_autorizacion.feature"
            )
            db.add(feature_solicitud)
            db.commit()
            db.refresh(feature_solicitud)
        
        feature_consulta = db.query(Feature).filter(
            Feature.name == "Consulta de Estado",
            Feature.application_id == app_autorizaciones.id
        ).first()
        if not feature_consulta:
            feature_consulta = Feature(
                name="Consulta de Estado",
                description="Consulta del estado de autorizaciones pendientes y procesadas",
                status=FeatureStatus.IN_DEVELOPMENT,
                application_id=app_autorizaciones.id,
                feature_file_path="features/consulta_estado.feature"
            )
            db.add(feature_consulta)
            db.commit()
            db.refresh(feature_consulta)
        
        print("✅ Features created")
        
        # Create test cases
        test_case_login = db.query(TestCase).filter(
            TestCase.name == "Login exitoso con credenciales válidas"
        ).first()
        if not test_case_login:
            test_case_login = TestCase(
                name="Login exitoso con credenciales válidas",
                description="Verificar que un usuario puede iniciar sesión con credenciales correctas",
                type=TestCaseType.AUTOMATED,
                priority=TestCasePriority.HIGH,
                status=TestCaseStatus.PRODUCTIVE,
                feature_id=feature_login.id,
                azure_user_story_id="US-1234",
                azure_user_story_url="https://dev.azure.com/empresa/proyecto/_workitems/edit/1234",
                azure_test_case_id="TC-5678",
                scenario_name="Login exitoso",
                tags=["login", "smoke", "critical"]
            )
            db.add(test_case_login)
            db.commit()
            db.refresh(test_case_login)
            
            # Add steps
            step1 = GherkinStep(
                test_case_id=test_case_login.id,
                type=GherkinStepType.GIVEN,
                text="el usuario se encuentra en la página de login",
                order=1
            )
            db.add(step1)
            db.commit()
            db.refresh(step1)
            
            db.add(GherkinSubStep(step_id=step1.id, text="Navegar a la URL del sistema", order=1))
            db.add(GherkinSubStep(step_id=step1.id, text="Verificar que la página de login está visible", order=2))
            
            step2 = GherkinStep(
                test_case_id=test_case_login.id,
                type=GherkinStepType.WHEN,
                text="ingresa credenciales válidas",
                order=2
            )
            db.add(step2)
            db.commit()
            db.refresh(step2)
            
            db.add(GherkinSubStep(step_id=step2.id, text="Ingresar usuario en el campo email", order=1))
            db.add(GherkinSubStep(step_id=step2.id, text="Ingresar contraseña en el campo password", order=2))
            db.add(GherkinSubStep(step_id=step2.id, text="Hacer clic en el botón Ingresar", order=3))
            
            step3 = GherkinStep(
                test_case_id=test_case_login.id,
                type=GherkinStepType.THEN,
                text="debe acceder al dashboard principal",
                order=3
            )
            db.add(step3)
            db.commit()
            db.refresh(step3)
            
            db.add(GherkinSubStep(step_id=step3.id, text="Verificar redirección al dashboard", order=1))
            db.add(GherkinSubStep(step_id=step3.id, text="Verificar que se muestra el nombre del usuario", order=2))
            
            db.commit()
        
        test_case_login_fallido = db.query(TestCase).filter(
            TestCase.name == "Login fallido con contraseña incorrecta"
        ).first()
        if not test_case_login_fallido:
            test_case_login_fallido = TestCase(
                name="Login fallido con contraseña incorrecta",
                description="Verificar mensaje de error cuando la contraseña es incorrecta",
                type=TestCaseType.AUTOMATED,
                priority=TestCasePriority.HIGH,
                status=TestCaseStatus.PRODUCTIVE,
                feature_id=feature_login.id,
                scenario_name="Login fallido - contraseña incorrecta",
                tags=["login", "negative"]
            )
            db.add(test_case_login_fallido)
            db.commit()
            db.refresh(test_case_login_fallido)
            
            db.add(GherkinStep(test_case_id=test_case_login_fallido.id, type=GherkinStepType.GIVEN, text="el usuario se encuentra en la página de login", order=1))
            db.add(GherkinStep(test_case_id=test_case_login_fallido.id, type=GherkinStepType.WHEN, text="ingresa un usuario válido pero contraseña incorrecta", order=2))
            db.add(GherkinStep(test_case_id=test_case_login_fallido.id, type=GherkinStepType.THEN, text='debe mostrar mensaje de error "Credenciales inválidas"', order=3))
            db.add(GherkinStep(test_case_id=test_case_login_fallido.id, type=GherkinStepType.AND, text="no debe permitir el acceso al sistema", order=4))
            db.commit()
        
        test_case_solicitud = db.query(TestCase).filter(
            TestCase.name == "Crear solicitud de autorización para consulta médica"
        ).first()
        if not test_case_solicitud:
            test_case_solicitud = TestCase(
                name="Crear solicitud de autorización para consulta médica",
                description="Verificar la creación de una solicitud de autorización para una consulta médica",
                type=TestCaseType.AUTOMATED,
                priority=TestCasePriority.HIGH,
                status=TestCaseStatus.PRODUCTIVE,
                feature_id=feature_solicitud.id,
                azure_user_story_id="US-2345",
                scenario_name="Solicitud autorización consulta",
                tags=["autorizacion", "consulta", "smoke"]
            )
            db.add(test_case_solicitud)
            db.commit()
            db.refresh(test_case_solicitud)
            
            db.add(GherkinStep(test_case_id=test_case_solicitud.id, type=GherkinStepType.GIVEN, text="el prestador está autenticado en el sistema", order=1))
            db.add(GherkinStep(test_case_id=test_case_solicitud.id, type=GherkinStepType.AND, text="tiene un socio con cobertura activa", order=2))
            db.add(GherkinStep(test_case_id=test_case_solicitud.id, type=GherkinStepType.WHEN, text="crea una solicitud de autorización para consulta médica", order=3))
            db.add(GherkinStep(test_case_id=test_case_solicitud.id, type=GherkinStepType.THEN, text='la solicitud debe quedar en estado "Pendiente"', order=4))
            db.add(GherkinStep(test_case_id=test_case_solicitud.id, type=GherkinStepType.AND, text="debe generar un número de trámite único", order=5))
            db.commit()
        
        print("✅ Test cases created")
        
        # Create a sample pipeline
        pipeline = db.query(GitlabPipeline).filter(
            GitlabPipeline.gitlab_project_id == "12345",
            GitlabPipeline.gitlab_pipeline_id == "98765"
        ).first()
        if not pipeline:
            pipeline = GitlabPipeline(
                gitlab_project_id="12345",
                gitlab_pipeline_id="98765",
                branch="main",
                status=PipelineStatus.PASSED,
                web_url="https://gitlab.com/empresa/autorizaciones/-/pipelines/98765",
                executed_at=datetime.utcnow()
            )
            db.add(pipeline)
            db.commit()
            db.refresh(pipeline)
            
            # Create pipeline results
            db.add(TestCasePipelineResult(
                test_case_id=test_case_login.id,
                pipeline_id=pipeline.id,
                status=TestCaseResultStatus.PASSED,
                duration=45
            ))
            db.add(TestCasePipelineResult(
                test_case_id=test_case_login_fallido.id,
                pipeline_id=pipeline.id,
                status=TestCaseResultStatus.PASSED,
                duration=32
            ))
            db.add(TestCasePipelineResult(
                test_case_id=test_case_solicitud.id,
                pipeline_id=pipeline.id,
                status=TestCaseResultStatus.PASSED,
                duration=78
            ))
            db.commit()
        
        print("✅ Pipeline and results created")
        
        # Create subscriptions
        sub_exists = db.query(GroupSubscription).filter(
            GroupSubscription.user_id == admin.id,
            GroupSubscription.group_id == group_salud.id
        ).first()
        if not sub_exists:
            db.add(GroupSubscription(user_id=admin.id, group_id=group_salud.id))
            db.add(GroupSubscription(user_id=admin.id, group_id=group_admin.id))
            db.add(GroupSubscription(user_id=user.id, group_id=group_salud.id))
            db.commit()
        
        print("✅ Subscriptions created")
        
        # Create a sample test request
        test_request = db.query(TestRequest).filter(
            TestRequest.title == "Automatizar validación de cobertura para estudios"
        ).first()
        if not test_request:
            test_request = TestRequest(
                title="Automatizar validación de cobertura para estudios",
                description="Necesitamos automatizar la validación de cobertura para diferentes tipos de estudios médicos. Actualmente este proceso se hace manualmente y queremos incluirlo en el pipeline de CI.",
                status=TestRequestStatus.NEW,
                application_id=app_autorizaciones.id,
                requester_id=user.id,
                azure_work_item_id="US-3456",
                azure_work_item_url="https://dev.azure.com/empresa/proyecto/_workitems/edit/3456"
            )
            db.add(test_request)
            db.commit()
        
        print("✅ Test request created")
        
        print("")
        print("🎉 Database seeding completed!")
        print("")
        print("📧 Default users:")
        print("   Admin: admin@docudash.com / admin123")
        print("   User:  usuario@docudash.com / user123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

