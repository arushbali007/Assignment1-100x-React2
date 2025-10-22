import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Bell, Clock, Calendar, Loader2, Save, ChevronLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

interface DeliverySettings {
  delivery_enabled: boolean;
  delivery_time: string;
  delivery_days: string;
  timezone: string;
}

export default function Settings() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [settings, setSettings] = useState<DeliverySettings>({
    delivery_enabled: true,
    delivery_time: "08:00:00",
    delivery_days: "weekdays",
    timezone: "UTC",
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem("authToken");
      const response = await fetch("http://localhost:8000/api/settings/delivery", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Failed to load settings");

      const data = await response.json();
      setSettings(data);
    } catch (error: any) {
      console.error("Failed to load settings:", error);
      toast.error("Failed to load settings");
    } finally {
      setIsLoading(false);
    }
  };

  const saveSettings = async () => {
    try {
      setIsSaving(true);
      const token = localStorage.getItem("authToken");
      const response = await fetch("http://localhost:8000/api/settings/delivery", {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          delivery_enabled: settings.delivery_enabled,
          delivery_time: settings.delivery_time,
          delivery_days: settings.delivery_days,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to save settings");
      }

      toast.success("Settings saved successfully!");
    } catch (error: any) {
      console.error("Failed to save settings:", error);
      toast.error(error.message || "Failed to save settings");
    } finally {
      setIsSaving(false);
    }
  };

  // Generate time options (6 AM to 11 PM)
  const timeOptions = [];
  for (let hour = 6; hour <= 23; hour++) {
    const time24 = `${hour.toString().padStart(2, "0")}:00:00`;
    const time12 = hour > 12 ? `${hour - 12}:00 PM` : hour === 12 ? "12:00 PM" : `${hour}:00 AM`;
    timeOptions.push({ value: time24, label: time12 });
  }

  const deliveryDaysOptions = [
    { value: "daily", label: "Every Day", description: "7 days a week" },
    { value: "weekdays", label: "Weekdays", description: "Monday - Friday" },
    { value: "weekends", label: "Weekends", description: "Saturday - Sunday" },
    { value: "Mon,Wed,Fri", label: "Mon, Wed, Fri", description: "3 days a week" },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/dashboard"
            className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4"
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Back to Dashboard
          </Link>
          <h1 className="text-4xl font-bold text-foreground mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Configure your morning delivery preferences
          </p>
        </div>

        {/* Morning Delivery Settings Card */}
        <Card className="p-6 mb-6">
          <div className="flex items-start gap-4 mb-6">
            <div className="p-3 bg-primary/10 rounded-lg">
              <Bell className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-1">Morning Delivery</h2>
              <p className="text-sm text-muted-foreground">
                Receive your newsletter draft and trending topics automatically via email
              </p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Enable/Disable Toggle */}
            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
              <div className="flex-1">
                <Label htmlFor="delivery-enabled" className="text-base font-medium">
                  Enable Morning Delivery
                </Label>
                <p className="text-sm text-muted-foreground mt-1">
                  {settings.delivery_enabled
                    ? "You'll receive daily newsletter emails"
                    : "Morning delivery is currently disabled"}
                </p>
              </div>
              <Switch
                id="delivery-enabled"
                checked={settings.delivery_enabled}
                onCheckedChange={(checked) =>
                  setSettings({ ...settings, delivery_enabled: checked })
                }
              />
            </div>

            {settings.delivery_enabled && (
              <>
                {/* Delivery Time */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-muted-foreground" />
                    <Label className="text-base font-medium">Delivery Time</Label>
                  </div>
                  <Select
                    value={settings.delivery_time}
                    onValueChange={(value) =>
                      setSettings({ ...settings, delivery_time: value })
                    }
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select time" />
                    </SelectTrigger>
                    <SelectContent>
                      {timeOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-muted-foreground">
                    Your newsletter will be sent at this time each day
                  </p>
                </div>

                {/* Delivery Days */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <Label className="text-base font-medium">Delivery Days</Label>
                  </div>
                  <Select
                    value={settings.delivery_days}
                    onValueChange={(value) =>
                      setSettings({ ...settings, delivery_days: value })
                    }
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select days" />
                    </SelectTrigger>
                    <SelectContent>
                      {deliveryDaysOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          <div>
                            <div className="font-medium">{option.label}</div>
                            <div className="text-xs text-muted-foreground">
                              {option.description}
                            </div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-muted-foreground">
                    Choose which days you want to receive your newsletter
                  </p>
                </div>

                {/* Timezone Info */}
                <div className="p-4 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900 rounded-lg">
                  <p className="text-sm text-blue-900 dark:text-blue-300">
                    <strong>Timezone:</strong> {settings.timezone}
                  </p>
                  <p className="text-xs text-blue-700 dark:text-blue-400 mt-1">
                    All delivery times are in UTC timezone
                  </p>
                </div>
              </>
            )}
          </div>

          {/* Save Button */}
          <div className="mt-6 flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={loadSettings}
              disabled={isSaving}
            >
              Cancel
            </Button>
            <Button
              onClick={saveSettings}
              disabled={isSaving}
              className="min-w-[120px]"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </Card>

        {/* Info Card */}
        <Card className="p-6 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20 border-purple-200 dark:border-purple-900">
          <h3 className="font-semibold mb-2 text-purple-900 dark:text-purple-300">
            📬 What's included in morning delivery?
          </h3>
          <ul className="space-y-2 text-sm text-purple-800 dark:text-purple-400">
            <li className="flex items-start gap-2">
              <span className="text-purple-500">•</span>
              <span>Your latest newsletter draft with AI-generated content</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-purple-500">•</span>
              <span>Top 3 trending topics from your sources</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-purple-500">•</span>
              <span>Beautiful HTML-formatted email delivered to your inbox</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-purple-500">•</span>
              <span>Quick links to review and send from your dashboard</span>
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
