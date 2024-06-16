import { Spotlight } from "./spotlight";

export function SpotlightPreview() {
    return (
        <div className="h-screen w-full rounded-md flex md:items-center md:justify-center  antialiased bg-grid-white/[0.02] relative overflow-hidden">
            <Spotlight
                className="-top-40 left-0 md:left-60 md:-top-20"
                fill="white"
            />
            <div className=" p-4 max-w-7xl  mx-auto relative z-10  w-full pt-20 md:pt-0">
                <h1 className="text-4xl md:text-7xl font-bold text-center bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
                    Real-time 3D POV
                </h1>
                <p className="mt-4 font-normal text-xl text-neutral-300 max-w-lg text-center mx-auto">
                    Step into the match with our AI-driven 3D POV experience.
                    Real-time insights, every angle. Perfect for fans, analysts,
                    and coaches. Revolutionize how you watch sports today!
                </p>
            </div>
        </div>
    );
}
