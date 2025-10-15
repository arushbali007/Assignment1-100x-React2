import { Link2, Brain, FileText, Send } from "lucide-react";

const steps = [
  {
    icon: Link2,
    title: "Connect Your Sources",
    description: "Link your favorite Twitter accounts, YouTube channels, and newsletter subscriptions.",
    step: "01",
  },
  {
    icon: Brain,
    title: "Train Your Voice",
    description: "Upload 20+ past newsletters so our AI learns your unique writing style and tone.",
    step: "02",
  },
  {
    icon: FileText,
    title: "Receive Daily Drafts",
    description: "Get a curated, voice-matched newsletter draft + trend highlights every morning at 8am.",
    step: "03",
  },
  {
    icon: Send,
    title: "Review & Send",
    description: "Quick 20-minute review, make any tweaks, and hit send. Track engagement in your analytics.",
    step: "04",
  },
];

export const HowItWorks = () => {
  return (
    <section className="py-24 bg-muted/30">
      <div className="container px-4 mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold mb-4">
            How CreatorPulse Works
          </h2>
          <p className="text-xl text-muted-foreground">
            Four simple steps to transform your newsletter workflow
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="text-center">
                <div className="relative inline-block mb-6">
                  <div className="absolute inset-0 bg-gradient-accent opacity-20 blur-2xl rounded-full" />
                  <div className="relative w-20 h-20 rounded-full bg-card border-2 border-primary/20 flex items-center justify-center mx-auto shadow-elevated">
                    <step.icon className="w-8 h-8 text-primary" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-primary text-primary-foreground text-xs font-bold flex items-center justify-center">
                    {step.step}
                  </div>
                </div>
                
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-muted-foreground">{step.description}</p>
              </div>
              
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-10 left-[60%] w-[80%] h-0.5 bg-gradient-to-r from-primary/50 to-transparent" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
