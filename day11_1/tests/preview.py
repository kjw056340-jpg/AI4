"""브라우저 레이아웃 점검 전용 서버. 실제 앱 실행에 사용하지 마세요.

python -m uvicorn tests.preview:preview --port 8000
실제 Supabase 연결 없이 공개 상품/폼 레이아웃을 검증합니다.
"""
from contextlib import asynccontextmanager
import os
os.environ.setdefault('APP_ORIGIN','http://127.0.0.1:8000')
from app.main import app
from tests.conftest import FakeDB


class PreviewDB(FakeDB):
    def select(self, table, **params):
        if table!='products':
            return super().select(table,**params)
        names=['모닝 세라믹 머그','포근한 테이블 램프','데일리 우드 체어','가벼운 캔버스 백','슬로우 월 클락','샌드 오브제 화병']
        prices=[18000,68000,129000,26000,42000,34000]
        categories=['키친','리빙','가구','라이프','리빙','리빙']
        keys=['mug','lamp','chair','bag','clock','vase']
        products=[{**self.product,'id':f'10000000-0000-4000-8000-{i+1:012d}','name':name,'price':prices[i],
                   'category':categories[i],'image_key':keys[i], 'description':'오래 곁에 두고 싶은 일상의 물건. 편안한 질감과 자연스러운 색감으로 공간에 따뜻함을 더합니다.'} for i,name in enumerate(names)]
        return [p for p in products if ('id' not in params or params['id']=='eq.'+p['id'])
                and ('category' not in params or params['category']=='eq.'+p['category'])]


@asynccontextmanager
async def lifespan(app):
    app.state.db=PreviewDB()
    yield


app.router.lifespan_context=lifespan
preview=app
