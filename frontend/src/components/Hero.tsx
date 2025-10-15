import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import heroImage from "@/assets/hero-image.jpg";

export const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-subtle">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,hsl(262_20%_95%)_1px,transparent_1px),linear-gradient(to_bottom,hsl(262_20%_95%)_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-30" />
      
      <div className="container relative z-10 px-4 py-20 mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm font-medium text-primary">
              <Sparkles className="w-4 h-4" />
              Cut your newsletter drafting time by 90%
            </div>
            
            <h1 className="text-5xl lg:text-7xl font-bold leading-tight">
              Your Daily Feed,
              <br />
              <span className="bg-gradient-accent bg-clip-text text-transparent">
                Curated & Drafted
              </span>
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-xl">
              CreatorPulse aggregates your trusted sources, detects emerging trends, and generates 
              newsletter drafts in your voice—delivered every morning at 8am.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/signup">
                <Button variant="hero" size="lg" className="group">
                  Start Free Trial
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <a href="#how-it-works">
                <Button variant="outline" size="lg">
                  Watch Demo
                </Button>
              </a>
            </div>
            
            <div className="flex items-center gap-8 pt-4">
              <div>
                <div className="text-3xl font-bold text-foreground">70%+</div>
                <div className="text-sm text-muted-foreground">Draft acceptance</div>
              </div>
              <div className="h-12 w-px bg-border" />
              <div>
                <div className="text-3xl font-bold text-foreground">&lt;20min</div>
                <div className="text-sm text-muted-foreground">Review time</div>
              </div>
              <div className="h-12 w-px bg-border" />
              <div>
                <div className="text-3xl font-bold text-foreground">2x</div>
                <div className="text-sm text-muted-foreground">Engagement uplift</div>
              </div>
            </div>
          </div>
          
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-primary opacity-20 blur-3xl rounded-full" />
            <img 
              src={heroImage} 
              alt="CreatorPulse Dashboard Preview" 
              className="relative rounded-2xl shadow-elevated w-full"
            />
          </div>
        </div>
      </div>
    </section>
  );
};
