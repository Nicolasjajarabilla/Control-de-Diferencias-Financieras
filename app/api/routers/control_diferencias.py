from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import file_processing_service
from io import BytesIO

router = APIRouter()

@router.post("/procesar-diferencias-condor-latin/")
async def procesar_diferencias_condor_latin(file_latin: UploadFile = File(...), file_argentina: UploadFile = File(...)):
    try:
        latin_bytes = await file_latin.read()
        argentina_bytes = await file_argentina.read()
        
        df_latin = file_processing_service.read_excel_from_bytes(BytesIO(latin_bytes))
        df_condor = file_processing_service.read_excel_from_bytes(BytesIO(argentina_bytes))

        resultados = file_processing_service.calculate_condor_latin_diff(df_latin, df_condor)
        
        return {"message": "Datos procesados exitosamente", "resultados": resultados}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/procesar-diferencias-condor-ibkr/")
async def procesar_diferencias_condor_ibkr(file_ibkr: UploadFile = File(...), file_condor: UploadFile = File(...)):
    try:
        ibkr_bytes = await file_ibkr.read()
        condor_bytes = await file_condor.read()

        resultados = file_processing_service.calculate_condor_ibkr_diff(ibkr_bytes, condor_bytes, file_ibkr.filename)
        
        return {"message": "Datos procesados exitosamente", "resultados": resultados}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/procesar-transactions-convers/")
async def procesar_transactions_convers(file_transactions: UploadFile = File(...), file_convers: UploadFile = File(...)):
    try:
        transactions_bytes = await file_transactions.read()
        convers_bytes = await file_convers.read()

        resultados = file_processing_service.calculate_transactions_convers_diff(
            transactions_bytes, 
            convers_bytes, 
            file_transactions.filename, 
            file_convers.filename
        )

        return {"message": "Todos los archivos fueron procesados exitosamente", "resultados": resultados}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
