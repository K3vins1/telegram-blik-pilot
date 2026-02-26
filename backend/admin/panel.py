from fastapi import APIRouter
router = APIRouter()
@router.get('/admin/payments')
def panel():
    return {'status': 'ok'}
