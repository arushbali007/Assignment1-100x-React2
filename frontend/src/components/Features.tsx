import { TrendingUp, Zap, Mail, ThumbsUp, BarChart3, Clock } from "lucide-react";
import { Card } from "@/components/ui/card";

const features = [
  {
    icon: Zap,
    title: "Multi-Source Aggregation",
    description: "Connect Twitter, YouTube, newsletters, and RSS feeds. We monitor your chosen sources 24/7.",
  },
  {
    icon: TrendingUp,
    title: "Trend Detection",
    description: "AI-powered spike detection surfaces emerging topics before they go mainstream.",
  },
  {
    icon: Mail,
    title: "Voice-Matched Drafts",
    description: "Upload past newsletters to train the AI. Get drafts that sound like you wrote them.",
  },
  {
    icon: Clock,
    title: "Morning Delivery",
    description: "Receive your draft newsletter and trends digest at 8am, ready for quick review.",
  },
  {
    icon: ThumbsUp,
    title: "Feedback Learning",
    description: "Thumbs up/down and edit tracking improves draft quality over time.",
  },
  {
    icon: BarChart3,
    title: "Engagement Analytics",
    description: "Track opens, clicks, and engagement to prove ROI and refine your strategy.",
  },
];

export const Features = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container px-4 mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold mb-4">
            Everything you need to scale your newsletter
          </h2>
          <p className="text-xl text-muted-foreground">
            From research to draft to delivery—all automated, all in your voice.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className="p-6 hover:shadow-elevated transition-all duration-300 border-2 hover:border-primary/50 group"
            >
              <div className="w-12 h-12 rounded-lg bg-gradient-primary flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                <feature.icon className="w-6 h-6 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
