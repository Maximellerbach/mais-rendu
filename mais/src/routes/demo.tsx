import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/demo")({
    component: Demo,
});

function mapKeyToDirection(key: string) {
    switch (key) {
        case "ArrowUp":
            return "FRONT";
        case "ArrowDown":
            return "BACK";
        case "ArrowLeft":
            return "LEFT";
        case "ArrowRight":
            return "RIGHT";
        case " ":
            return "UP";
        case "Shift":
            return "DOWN";
        default:
            return null;
    }
}

function Demo() {
    const [image, setImage] = useState<string | null>(null);

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8765");

        socket.onopen = () => {
            console.log("WebSocket connection established");
        };

        socket.onmessage = (event) => {
            const data = event.data;
            console.log(data);
            // if (data instanceof Blob) {
                // const url = URL.createObjectURL(data);
                // setImage(url);
            // }

            const base64Image = "data:image/jpeg;base64," + data;
            setImage(base64Image);
        };

        socket.onclose = () => {
            console.log("WebSocket connection closed");
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        const handleKeyDown = (event) => {
            // socket.send(JSON.stringify({ type: "keyEvent", key: event.key }));
            const direction = mapKeyToDirection(event.key);
            console.log(direction);
            socket.send(direction);
        };

        window.addEventListener("keydown", handleKeyDown);

        const t = setInterval(() => {
            // send empty event every 1s to keep connection alive
            socket?.send("");
        }, 200);

        return () => {
            socket.close();
            window.removeEventListener("keydown", handleKeyDown);
            clearInterval(t);
        };
    }, []);


    return (
        <div className="bg-white h-screen w-screen flex justify-center item-center">
            {image && <img src={image} 
                className="h-screen"
            />}
        </div>
    );
}
