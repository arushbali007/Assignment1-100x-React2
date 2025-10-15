import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Twitter,
  Youtube,
  Mail as MailIcon,
  Plus,
  Settings,
  TrendingUp,
  CheckCircle2,
  Loader2,
  Rss,
  Trash2,
  User,
  LogOut,
  HelpCircle,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { sourcesApi } from "@/lib/api";
import { toast } from "sonner";

const sourceIcons = {
  twitter: Twitter,
  youtube: Youtube,
  newsletter: MailIcon,
  rss: Rss,
};

const sourceColors = {
  twitter: { bg: "bg-blue-500/10", text: "text-blue-500" },
  youtube: { bg: "bg-red-500/10", text: "text-red-500" },
  newsletter: { bg: "bg-purple-500/10", text: "text-purple-500" },
  rss: { bg: "bg-orange-500/10", text: "text-orange-500" },
};

export default function Sources() {
  const { user, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [sources, setSources] = useState<any[]>([]);
  const [stats, setStats] = useState({ total: 0, twitter: 0, youtube: 0, rss: 0, newsletter: 0 });
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    source_type: "twitter",
    source_url: "",
    name: "",
    metadata: {} as any,
    is_active: true,
  });

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      setIsLoading(true);
      const [sourcesResponse, statsResponse] = await Promise.all([
        sourcesApi.getAll(),
        sourcesApi.getStats(),
      ]);

      setSources(sourcesResponse.sources || []);
      setStats(statsResponse);
    } catch (error: any) {
      console.error("Failed to load sources:", error);
      toast.error("Failed to load sources");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddSource = async () => {
    if (!formData.source_url || !formData.name) {
      toast.error("Please fill in source URL and name");
      return;
    }

    setIsSubmitting(true);
    try {
      await sourcesApi.create(formData);
      toast.success("Source added successfully!");
      setIsAddDialogOpen(false);

      // Reset form
      setFormData({
        source_type: "twitter",
        source_url: "",
        name: "",
        metadata: {},
        is_active: true,
      });

      // Reload sources
      await loadSources();
    } catch (error: any) {
      console.error("Add source error:", error);
      const errorMessage = error?.message || error?.detail || "Failed to add source";
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteSource = async (sourceId: string, sourceName: string) => {
    if (!confirm(`Are you sure you want to delete ${sourceName}?`)) {
      return;
    }

    // Optimistic UI update - remove from list immediately
    const originalSources = [...sources];
    const originalStats = { ...stats };

    try {
      // Update UI optimistically
      setSources(sources.filter(s => s.id !== sourceId));

      // Make API call
      await sourcesApi.delete(sourceId);

      // Reload to get fresh data and stats
      await loadSources();
      toast.success("Source deleted successfully!");
    } catch (error: any) {
      // Rollback on error
      setSources(originalSources);
      setStats(originalStats);

      console.error("Delete source error:", error);
      const errorMessage = error?.message || error?.detail || "Failed to delete source";
      toast.error(errorMessage);
    }
  };

  const handleToggleActive = async (sourceId: string, currentStatus: boolean) => {
    try {
      await sourcesApi.update(sourceId, { is_active: !currentStatus });
      toast.success(`Source ${!currentStatus ? "activated" : "paused"}`);
      await loadSources();
    } catch (error: any) {
      console.error("Toggle source error:", error);
      const errorMessage = error?.message || error?.detail || "Failed to update source";
      toast.error(errorMessage);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
          <p className="mt-4 text-muted-foreground">Loading sources...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <header className="border-b border-border/40 backdrop-blur-xl bg-background/80">
        <div className="container px-4 mx-auto">
          <div className="flex items-center justify-between h-16">
            <Link to="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
                <MailIcon className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">CreatorPulse</span>
            </Link>

            <nav className="hidden md:flex items-center gap-6">
              <Link to="/dashboard" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                Dashboard
              </Link>
              <Link to="/sources" className="text-sm font-medium text-foreground">
                Sources
              </Link>
              <Link to="/drafts" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                Drafts
              </Link>
            </nav>

            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground hidden md:inline">
                {user?.email}
              </span>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <Settings className="w-5 h-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>Account Settings</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <User className="w-4 h-4 mr-2" />
                    <span>Profile</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => window.open('https://docs.creatorpulse.com', '_blank')}>
                    <HelpCircle className="w-4 h-4 mr-2" />
                    <span>Help & Documentation</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={logout} className="text-red-600 focus:text-red-600">
                    <LogOut className="w-4 h-4 mr-2" />
                    <span>Logout</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container px-4 mx-auto py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Content Sources</h1>
            <p className="text-muted-foreground">
              Manage the sources CreatorPulse monitors for your newsletter
            </p>
          </div>
          <Button variant="hero" onClick={() => setIsAddDialogOpen(true)}>
            <Plus className="w-5 h-5 mr-2" />
            Add Source
          </Button>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 border-2 hover:border-primary/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm">Total Sources</span>
              <TrendingUp className="w-5 h-5 text-primary" />
            </div>
            <div className="text-3xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {sources.filter((s) => s.is_active).length} active
            </p>
          </Card>

          <Card className="p-6 border-2 hover:border-primary/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm">Twitter</span>
              <Twitter className="w-5 h-5 text-blue-500" />
            </div>
            <div className="text-3xl font-bold">{stats.twitter}</div>
            <p className="text-xs text-muted-foreground mt-1">accounts</p>
          </Card>

          <Card className="p-6 border-2 hover:border-primary/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm">YouTube</span>
              <Youtube className="w-5 h-5 text-red-500" />
            </div>
            <div className="text-3xl font-bold">{stats.youtube}</div>
            <p className="text-xs text-muted-foreground mt-1">channels</p>
          </Card>

          <Card className="p-6 border-2 hover:border-primary/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm">RSS Feeds</span>
              <Rss className="w-5 h-5 text-orange-500" />
            </div>
            <div className="text-3xl font-bold">{stats.rss}</div>
            <p className="text-xs text-muted-foreground mt-1">feeds</p>
          </Card>
        </div>

        {/* Sources List */}
        {sources.length === 0 ? (
          <Card className="p-16 border-2 text-center bg-muted/30">
            <TrendingUp className="w-20 h-20 mx-auto text-muted-foreground mb-6" />
            <h2 className="text-2xl font-bold mb-3">No Sources Yet</h2>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Start by adding your first content source. Connect Twitter accounts, YouTube channels, RSS feeds, or newsletter subscriptions.
            </p>
            <Button variant="hero" size="lg" onClick={() => setIsAddDialogOpen(true)}>
              <Plus className="w-5 h-5 mr-2" />
              Add Your First Source
            </Button>
          </Card>
        ) : (
          <div className="space-y-4">
            {sources.map((source) => {
              const Icon = sourceIcons[source.source_type as keyof typeof sourceIcons] || Rss;
              const colors = sourceColors[source.source_type as keyof typeof sourceColors] || sourceColors.rss;

              return (
                <Card
                  key={source.id}
                  className="p-6 border-2 hover:border-primary/50 transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${colors.bg}`}>
                        <Icon className={`w-6 h-6 ${colors.text}`} />
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="text-lg font-semibold">{source.name}</h3>
                          <Badge variant={source.is_active ? "default" : "secondary"}>
                            {source.is_active ? "Active" : "Paused"}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="capitalize">{source.source_type}</span>
                          <span>•</span>
                          <span>{source.source_identifier}</span>
                          {source.category && (
                            <>
                              <span>•</span>
                              <span>{source.category}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleToggleActive(source.id, source.is_active)}
                        title={source.is_active ? "Pause source" : "Activate source"}
                      >
                        <CheckCircle2
                          className={`w-5 h-5 ${source.is_active ? "text-green-500" : "text-muted-foreground"}`}
                        />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-destructive hover:text-destructive hover:bg-destructive/10"
                        onClick={() => handleDeleteSource(source.id, source.name)}
                      >
                        <Trash2 className="w-5 h-5" />
                      </Button>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </main>

      {/* Add Source Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="sm:max-w-[525px]">
          <DialogHeader>
            <DialogTitle>Add New Source</DialogTitle>
            <DialogDescription>
              Connect a new content source to monitor for your newsletter.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="source_type">Source Type</Label>
              <Select
                value={formData.source_type}
                onValueChange={(value) =>
                  setFormData({ ...formData, source_type: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="twitter">Twitter Account</SelectItem>
                  <SelectItem value="youtube">YouTube Channel</SelectItem>
                  <SelectItem value="rss">RSS Feed</SelectItem>
                  <SelectItem value="newsletter">Newsletter</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="source_url">
                {formData.source_type === "twitter" && "Twitter Profile URL"}
                {formData.source_type === "youtube" && "YouTube Channel URL"}
                {formData.source_type === "rss" && "RSS Feed URL"}
                {formData.source_type === "newsletter" && "Newsletter URL"}
              </Label>
              <Input
                id="source_url"
                placeholder={
                  formData.source_type === "twitter"
                    ? "https://twitter.com/username"
                    : formData.source_type === "youtube"
                    ? "https://youtube.com/@channel"
                    : formData.source_type === "rss"
                    ? "https://example.com/feed"
                    : "https://newsletter.example.com"
                }
                value={formData.source_url}
                onChange={(e) =>
                  setFormData({ ...formData, source_url: e.target.value })
                }
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="name">Display Name</Label>
              <Input
                id="name"
                placeholder="My Favorite Source"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </div>

          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="hero"
              onClick={handleAddSource}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Adding...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Source
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
