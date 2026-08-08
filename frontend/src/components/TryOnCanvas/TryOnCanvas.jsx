import { useEffect, useMemo, useState } from "react";
import CategorySelector from "./CategorySelector";
import { fetchWardrobe, getTryOnImageUrl } from "../../api/client";
import "./TryOnCanvas.css";

const CATEGORY_ORDER = ["top", "bottom", "shoes"];
const CATEGORY_LABELS = {
  top: "Góra",
  bottom: "Dół",
  shoes: "Buty",
};

export default function TryOnCanvas({ userId }) {
  const [wardrobe, setWardrobe] = useState([]);
  const [selectedIndexByCategory, setSelectedIndexByCategory] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    fetchWardrobe(userId)
      .then((items) => {
        if (cancelled) return;
        setWardrobe(items);
        const initialSelection = {};
        CATEGORY_ORDER.forEach((cat) => {
          const firstIndex = items.findIndex((item) => item.category === cat);
          if (firstIndex !== -1) initialSelection[cat] = 0;
        });
        setSelectedIndexByCategory(initialSelection);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Nie udało się pobrać szafy");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [userId]);

  const itemsByCategory = useMemo(() => {
    const grouped = {};
    CATEGORY_ORDER.forEach((cat) => {
      grouped[cat] = wardrobe.filter((item) => item.category === cat);
    });
    return grouped;
  }, [wardrobe]);

  const selectedItemIds = useMemo(() => {
    return CATEGORY_ORDER.filter(
      (cat) => selectedIndexByCategory[cat] !== undefined && itemsByCategory[cat]?.length > 0
    ).map((cat) => itemsByCategory[cat][selectedIndexByCategory[cat]].id);
  }, [selectedIndexByCategory, itemsByCategory]);

  const tryOnImageUrl = useMemo(() => {
    if (selectedItemIds.length === 0) return null;
    return getTryOnImageUrl(userId, selectedItemIds);
  }, [userId, selectedItemIds]);

  const handleCategoryChange = (category, newIndex) => {
    setSelectedIndexByCategory((prev) => ({ ...prev, [category]: newIndex }));
  };

  if (loading) return <div className="tryon-canvas__status">Ładowanie szafy...</div>;
  if (error) return <div className="tryon-canvas__status tryon-canvas__status--error">{error}</div>;

  return (
    <div className="tryon-canvas">
      <div className="tryon-canvas__preview">
        {tryOnImageUrl ? (
          <img
            key={tryOnImageUrl}
            src={tryOnImageUrl}
            alt="Podgląd przymierzanego outfitu"
            className="tryon-canvas__image"
          />
        ) : (
          <div className="tryon-canvas__status">Dodaj ubrania do szafy, żeby zacząć</div>
        )}
      </div>

      <div className="tryon-canvas__selectors">
        {CATEGORY_ORDER.map((cat) => (
          <CategorySelector
            key={cat}
            label={CATEGORY_LABELS[cat]}
            items={itemsByCategory[cat] || []}
            selectedIndex={selectedIndexByCategory[cat] ?? 0}
            onChange={(newIndex) => handleCategoryChange(cat, newIndex)}
          />
        ))}
      </div>
    </div>
  );
}