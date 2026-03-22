# Quy Tắc Code — Backend (FastAPI)

> Đọc rules gốc tại `../../.claude/rules/CODE_RULES.md` trước.
> File này bổ sung quy tắc RIÊNG cho Backend.

---

## Cấm Tuyệt Đối (Vi phạm = revert ngay)

```python
# ❌ 1. CORSMiddleware — Gateway xử lý
app.add_middleware(CORSMiddleware)  # XÓA NGAY

# ❌ 2. Trả ORM model trực tiếp
@router.get("/users/{id}")
async def get_user(id: int, db = Depends(get_db)):
    return await db.get(User, id)  # RÒ RỈ NỘI BỘ

# ❌ 3. Sync trong async
async def get_data():
    response = requests.get(url)    # BLOCK EVENT LOOP
    time.sleep(5)                   # BLOCK EVENT LOOP
    data = open("file.txt").read()  # BLOCK I/O

# ❌ 4. Business logic trong router
@router.post("/users")
async def create_user(data: UserCreate, db = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar():
        raise HTTPException(409, "Email exists")  # LOGIC TRONG ROUTER
    user = User(**data.model_dump())
    # ... 20 dòng logic nữa

# ❌ 5. Raw SQL với f-string
await db.execute(text(f"SELECT * FROM users WHERE email = '{email}'"))  # SQL INJECTION

# ❌ 6. Catch Exception chung rồi nuốt
try:
    await do_something()
except Exception:
    pass  # NUỐT LỖI

# ❌ 7. print() thay vì logger
print(f"User created: {user.id}")  # KHÔNG CÓ CONTEXT, KHÔNG JSON
```

---

## Mẫu Đúng (Copy từ đây)

### File mới: endpoint + service + repository

```python
# app/api/v1/products.py — Router (mỏng, chỉ validate + delegate)
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int = Path(ge=1),
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    return await service.get_product(product_id)

@router.get("/", response_model=PaginatedResponse[ProductResponse])
async def list_products(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    category_id: int | None = Query(default=None),
    service: ProductService = Depends(get_product_service),
) -> PaginatedResponse[ProductResponse]:
    return await service.list_products(page=page, size=size, category_id=category_id)

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    return await service.create_product(data, created_by=current_user.id)
```

```python
# app/services/product.py — Service (business logic)
class ProductService:
    def __init__(self, repo: ProductRepository, category_repo: CategoryRepository):
        self.repo = repo
        self.category_repo = category_repo

    async def create_product(self, data: ProductCreate, created_by: int) -> Product:
        category = await self.category_repo.get_by_id(data.category_id)
        if not category:
            raise NotFoundError("category", data.category_id)
        slug = slugify(data.name)
        existing = await self.repo.get_by_slug(slug)
        if existing:
            raise DuplicateError("product", "slug", slug)
        product = Product(**data.model_dump(), slug=slug, created_by=created_by)
        return await self.repo.create(product)
```

```python
# app/repositories/product.py — Repository (data access thuần)
class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def list(
        self, *, offset: int = 0, limit: int = 20, category_id: int | None = None
    ) -> tuple[list[Product], int]:
        query = select(Product).options(selectinload(Product.category))
        if category_id:
            query = query.where(Product.category_id == category_id)
        count = (await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )).scalar_one()
        items = (await self.session.execute(
            query.offset(offset).limit(limit).order_by(Product.created_at.desc())
        )).scalars().all()
        return list(items), count
```

### Dependency injection chain
```python
# app/dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            yield session

async def get_product_repo(db: AsyncSession = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)

async def get_category_repo(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)

async def get_product_service(
    repo: ProductRepository = Depends(get_product_repo),
    category_repo: CategoryRepository = Depends(get_category_repo),
) -> ProductService:
    return ProductService(repo, category_repo)
```

### Pydantic schema với camelCase output
```python
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

class ProductCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    price: Decimal = Field(ge=0, decimal_places=2)
    category_id: int = Field(ge=1)

class ProductResponse(BaseSchema):
    id: int
    name: str
    slug: str
    price: Decimal
    is_active: bool
    category_id: int
    created_at: datetime
```

---

## Checklist Trước Khi Commit

```bash
ruff check .                    # Lint sạch
mypy . --strict                 # Type check sạch
pytest --cov=app --cov-fail-under=80  # Coverage >= 80%
bandit -r app/ -q               # Không security issue
grep -rn "CORSMiddleware" app/  # Phải trả về trống
grep -rn "import requests" app/ # Phải trả về trống (dùng httpx)
grep -rn "print(" app/          # Phải trả về trống (dùng structlog)
```
