import "./App.css";
import Home from "./pages/Home";
import Header from "./components/Header";
import Footer from "./components/Footer";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Search from "./components/Search";
import ProductDetail from "./pages/Productdetail";
import { useState } from "react";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Cart from "./pages/Cart";

function App() {
  const [cartItems, setCartItems] = useState([]);

  return (
    <Router>
      <div className="App">
        <ToastContainer theme="dark" position="top-center"/>
        <Header cartItems={cartItems} />

        <div>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<Home />} />
            <Route
              path="/product/:id"
              element={
                <ProductDetail
                  cartItems={cartItems}
                  setCartItems={setCartItems}
                />
              }
            />
            <Route
              path="/cart"
              element={
                <Cart cartItems={cartItems} setCartItems={setCartItems} />
              }
            />
              
            
          </Routes>
        </div>

        {/* <h1>Welcome to the React Frontend!</h1> */}
        <Footer />
      </div>
    </Router>
  );
}

export default App;
