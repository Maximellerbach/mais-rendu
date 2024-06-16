import { createFileRoute } from "@tanstack/react-router";
import { MacbookScroll } from "../components/macbook";
import { SpotlightPreview } from "../components/header2";
import { Card } from "../components/card";

export const Route = createFileRoute("/")({
    component: Index,
});

function Index() {
    return (
        <div className="bg-black">
            {/* <SparklesPreview /> */}
            <SpotlightPreview />
            <MacbookScroll title="Next-Gen Sports Immersion" />
            <Card />
            <div className="h-[20vh] w-full" />
        </div>
    );
}
