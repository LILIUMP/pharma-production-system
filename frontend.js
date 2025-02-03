import React, { useEffect, useState } from "react";

const ProductionOrders = () => {
  const [orders, setOrders] = useState([]);
  const [productName, setProductName] = useState("");
  const [quantity, setQuantity] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/get_production_orders/")
      .then((res) => res.json())
      .then((data) => setOrders(data));
  }, []);

  const handleCreateOrder = () => {
    fetch("http://localhost:8000/create_production_order/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_name: productName,
        quantity_required: parseFloat(quantity),
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setOrders([...orders, { id: data.order_id, product_name: productName, quantity_required: quantity }]);
        setProductName("");
        setQuantity("");
      });
  };

  return (
    <div>
      <h1>أوامر الإنتاج</h1>
      <input
        type="text"
        placeholder="اسم المنتج"
        value={productName}
        onChange={(e) => setProductName(e.target.value)}
      />
      <input
        type="number"
        placeholder="الكمية المطلوبة"
        value={quantity}
        onChange={(e) => setQuantity(e.target.value)}
      />
      <button onClick={handleCreateOrder}>إنشاء أمر إنتاج</button>

      <ul>
        {orders.map((order) => (
          <li key={order.id}>{order.product_name} - {order.quantity_required}</li>
        ))}
      </ul>
    </div>
  );
};

export default ProductionOrders;
