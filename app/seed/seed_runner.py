from app.db.base import Base
from app.db.models import Assembly, BomItem, Component
from app.db.session import engine, SessionLocal


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        if session.query(Component).count() > 0:
            return
        c1 = Component(component_code="R-14", name="Resistor 10k", description="10k resistor", component_type="resistor", attributes_json={"tolerance": "1%"})
        c2 = Component(component_code="C-102", name="Capacitor 1uF", description="1uF capacitor", component_type="capacitor", attributes_json={"voltage": "16V"})
        a1 = Assembly(assembly_code="A-1000", name="Controller Board", description="Main board")
        session.add_all([c1, c2, a1])
        session.flush()
        session.add_all([
            BomItem(assembly_id=a1.id, component_id=c1.id, quantity=4, reference_designator="R1,R2,R3,R4"),
            BomItem(assembly_id=a1.id, component_id=c2.id, quantity=2, reference_designator="C1,C2"),
        ])
        session.commit()


if __name__ == "__main__":
    run_seed()
