import TryOnCanvas from "./components/TryOnCanvas/TryOnCanvas";
import "./App.css";

const TEST_USER_ID = "9793f4cb-8c6a-4845-bb5c-424545580c58";

function App() {
  return (
    <div className="app">
      <h1 className="app__title">Virtual Closet — Przymierzalnia</h1>
      <TryOnCanvas userId={TEST_USER_ID} />
    </div>
  );
}

export default App;