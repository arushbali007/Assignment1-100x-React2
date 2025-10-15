import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Check } from "lucide-react";
import { Link } from "react-router-dom";

const plans = [
  {
    name: "Starter",
    price: "$29",
    period: "per month",
    description: "Perfect for individual creators",
    features: [
      "Up to 10 sources",
      "Daily newsletter drafts",
      "Voice training (20+ samples)",
      "Trend detection",
      "Email delivery",
      "Basic analytics",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$79",
    period: "per month",
    description: "For serious content curators",
    features: [
      "Unlimited sources",
      "Daily newsletter drafts",
      "Advanced voice training",
      "Priority trend detection",
      "Email + WhatsApp delivery",
      "Advanced analytics",
      "Custom delivery time",
      "API access",
    ],
    cta: "Start Free Trial",
    highlighted: true,
  },
  {
    name: "Agency",
    price: "Custom",
    period: "usage-based",
    description: "For agencies managing multiple newsletters",
    features: [
      "Everything in Pro",
      "Multi-client management",
      "White-label options",
      "Dedicated support",
      "Custom integrations",
      "Volume discounts",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
];

export const Pricing = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container px-4 mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-muted-foreground">
            Choose the plan that fits your workflow. All plans include a 14-day free trial.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <Card 
              key={index} 
              className={`p-8 relative ${
                plan.highlighted 
                  ? 'border-2 border-primary shadow-glow scale-105' 
                  : 'border-2 hover:border-primary/50'
              } transition-all duration-300`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-accent rounded-full text-sm font-semibold text-primary-foreground">
                  Most Popular
                </div>
              )}
              
              <div className="mb-6">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-muted-foreground text-sm mb-4">{plan.description}</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold">{plan.price}</span>
                  <span className="text-muted-foreground">{plan.period}</span>
                </div>
              </div>
              
              {plan.cta === "Contact Sales" ? (
                <a href="mailto:sales@creatorpulse.com">
                  <Button
                    variant={plan.highlighted ? "hero" : "outline"}
                    className="w-full mb-6"
                  >
                    {plan.cta}
                  </Button>
                </a>
              ) : (
                <Link to="/signup">
                  <Button
                    variant={plan.highlighted ? "hero" : "outline"}
                    className="w-full mb-6"
                  >
                    {plan.cta}
                  </Button>
                </Link>
              )}
              
              <div className="space-y-3">
                {plan.features.map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check className="w-3 h-3 text-primary" />
                    </div>
                    <span className="text-sm text-muted-foreground">{feature}</span>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};
