import { Fragment, useEffect, useState } from "react";
import ProductsCard from "../components/ProductsCard";
import { useSearchParams } from "react-router-dom";

export default function Home() {
  const [products, setProducts] = useState([]);
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    fetch(process.env.REACT_APP_API_URL + "/api/v1/products?" + searchParams)
      .then((res) => res.json())
      .then((res) => {
        console.log(res);
        setProducts(res.product);
      });
  }, [searchParams]);

  return (
    <Fragment>
      <h1 id="products_heading">Latest Products</h1>

      <section id="products" className="container mt-5">
        <div className="row">
          {products.map((product) => (
            <ProductsCard key={product._id} product={product} />
          ))}
        </div>
      </section>
    </Fragment>
  );
}
