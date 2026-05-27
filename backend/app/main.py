from fastapi import FastAPI, HTTPException
from faker import Faker
import random

app = FastAPI(
    title="API de Facturas Fake",
    version="1.0",
    description="API para generación de facturas sintéticas usando Faker"
)

fake = Faker("es_ES")


@app.get("/")
def home():
    return {
        "mensaje": "API de Facturas funcionando correctamente"
    }


@app.get("/facturas/v1/{numero_factura}", tags=["Facturas"])
def get_factura(numero_factura: str):

    # Validación básica
    if len(numero_factura.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="El número de factura es obligatorio"
        )

    # Datos empresa
    empresa = {
        "nombre": fake.company(),
        "nit": fake.bothify(text="#########"),
        "direccion": fake.address(),
        "telefono": fake.phone_number(),
        "email": fake.company_email()
    }

    # Datos cliente
    cliente = {
        "nombre": fake.company(),
        "nit": fake.bothify(text="#########"),
        "direccion": fake.address(),
        "telefono": fake.phone_number(),
        "email": fake.email()
    }

    # Generar detalle de productos
    detalle = []

    cantidad_items = random.randint(1, 5)

    for _ in range(cantidad_items):

        cantidad = random.randint(1, 10)

        precio_unitario = round(
            random.uniform(50, 500),
            2
        )

        total_item = round(
            cantidad * precio_unitario,
            2
        )

        detalle.append({
            "descripcion": fake.catch_phrase(),
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "total": total_item
        })

    # Cálculos
    subtotal = round(
        sum(item["total"] for item in detalle),
        2
    )

    impuesto = round(subtotal * 0.21, 2)

    total = round(subtotal + impuesto, 2)

    # Factura final
    factura = {
        "numero_factura": numero_factura,
        "fecha_emision": str(
            fake.date_between(
                start_date="-1y",
                end_date="today"
            )
        ),
        "moneda": "EUR",
        "empresa": empresa,
        "cliente": cliente,
        "cantidad_items": cantidad_items,
        "detalle": detalle,
        "subtotal": subtotal,
        "impuesto": impuesto,
        "total": total
    }

    return factura