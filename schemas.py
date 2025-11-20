"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class AthProduct(BaseModel):
    """
    Athleisure Products collection schema
    Collection name: "athproduct" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    gender: str = Field(..., description="Target gender: men, women, or unisex")
    category: str = Field(..., description="Category like leggings, joggers, tops, sports-bra")
    colors: List[str] = Field(default_factory=list, description="Available color names")
    sizes: List[str] = Field(default_factory=list, description="Available sizes")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    tags: List[str] = Field(default_factory=list, description="Search tags and highlights")
    in_stock: bool = Field(True, description="Whether product is in stock")

# The Flames database viewer can introspect these schemas via /schema endpoint in main.py
