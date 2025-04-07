from typing import Generic, Type, TypeVar, Optional, List, Dict, Any, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import as_declarative, declared_attr

# Definimos tipos genéricos
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUDBase con métodos genéricos para modelos SQLAlchemy.
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        try:
            # Loguea los datos de entrada
            
            # Convierte a diccionario, excluyendo valores no establecidos
            obj_in_data = obj_in.dict(exclude_unset=True)
            
            # Loguea el diccionario resultante
            
            # Crea el objeto
            db_obj = self.model(**obj_in_data)
            
            # Loguea el objeto antes de guardar
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            # Loguea el objeto después de guardar
            
            return db_obj
        
        except Exception as e:
            # Loguea cualquier error
            raise

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True) if isinstance(obj_in, BaseModel) else obj_in
        for field in obj_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: Any) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
