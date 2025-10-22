import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  FileText,
  TrendingUp,
  Mail,
  Settings,
  Plus,
  Calendar,
  BarChart3,
  Clock,
  CheckCircle2,
  Loader2,
  User,
  LogOut,
  HelpCircle,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { draftsApi, trendsApi, sourcesApi, newsletterSendsApi, contentApi } from "@/lib/api";
import { toast } from "sonner";

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    draftsThisWeek: 0,
    acceptanceRate: 0,
    avgReviewTime: "0m",
    engagement: "0x",
  });
  const [recentDrafts, setRecentDrafts] = useState<any[]>([]);
  const [sourceCount, setSourceCount] = useState(0);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);

      // Format time as "Xm Ys" for better visibility
      const formatTime = (seconds: number) => {
        if (!seconds || seconds === 0) return "0m 0s";
        const mins = Math.floor(seconds / 60);
        const secs = Math.round(seconds % 60);
        return `${mins}m ${secs}s`;
      };

      // Fetch only essential data in parallel
      const [draftStats, sendStats, draftsResponse, sourcesStats] =
        await Promise.all([
          draftsApi.getStats(),
          newsletterSendsApi.getStats(),
          draftsApi.getAll(1, 3), // Get recent 3 drafts
          sourcesApi.getStats(),   // Get source count
        ]);

      // Process stats
      setStats({
        draftsThisWeek: draftStats.total_drafts || 0,
        acceptanceRate: sendStats.successful_sends > 0
          ? Math.round((sendStats.successful_sends / sendStats.total_sends) * 100)
          : 85, // Default
        avgReviewTime: draftStats.avg_review_time_minutes
          ? `${Math.floor(draftStats.avg_review_time_minutes)}m`
          : draftStats.avg_generation_time
          ? formatTime(draftStats.avg_generation_time)
          : "18m 0s",
        engagement: sendStats.open_rate > 0
          ? `${(sendStats.open_rate / 50).toFixed(1)}x`
          : "2.1x", // Default
      });

      setRecentDrafts(draftsResponse.drafts || []);
      setSourceCount(sourcesStats.total || 0);
    } catch (error: any) {
      console.error("Failed to load dashboard:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary" />
          <p className="mt-4 text-muted-foreground">Loading dashboard...</p>
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
                <Mail className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">CreatorPulse</span>
            </Link>
            
            <nav className="hidden md:flex items-center gap-6">
              <Link to="/dashboard" className="text-sm font-medium text-foreground">
                Dashboard
              </Link>
              <Link to="/sources" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
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
        {/* Welcome Banner for New Users - Only show if no sources */}
        {sourceCount === 0 && recentDrafts.length === 0 && (
          <Card className="p-8 mb-8 border-2 border-primary/50 bg-gradient-to-r from-primary/5 to-secondary/5">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex-1">
                <h2 className="text-2xl font-bold mb-2">
                  👋 Welcome to CreatorPulse!
                </h2>
                <p className="text-muted-foreground mb-4">
                  Get started by adding your content sources. Then generate your first AI-powered newsletter draft!
                </p>
                <div className="flex flex-wrap gap-3">
                  <Link to="/sources">
                    <Button variant="hero" size="lg">
                      <Plus className="w-5 h-5 mr-2" />
                      Add Your First Source
                    </Button>
                  </Link>
                  <a href="#how-to-start">
                    <Button variant="outline" size="lg">
                      Quick Start Guide
                    </Button>
                  </a>
                </div>
              </div>
              <div className="w-32 h-32 rounded-full bg-gradient-primary flex items-center justify-center">
                <Mail className="w-16 h-16 text-primary-foreground" />
              </div>
            </div>
          </Card>
        )}

        {/* Banner for users with sources but no drafts */}
        {sourceCount > 0 && recentDrafts.length === 0 && (
          <Card className="p-8 mb-8 border-2 border-primary/50 bg-gradient-to-r from-primary/5 to-secondary/5">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex-1">
                <h2 className="text-2xl font-bold mb-2">
                  🎉 Great! You have {sourceCount} source{sourceCount !== 1 ? 's' : ''} connected
                </h2>
                <p className="text-muted-foreground mb-4">
                  Now generate your first AI-powered newsletter draft from your sources!
                </p>
                <div className="flex flex-wrap gap-3">
                  <Link to="/drafts">
                    <Button variant="hero" size="lg">
                      <Plus className="w-5 h-5 mr-2" />
                      Generate Your First Draft
                    </Button>
                  </Link>
                  <Link to="/sources">
                    <Button variant="outline" size="lg">
                      Manage Sources
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="w-32 h-32 rounded-full bg-gradient-primary flex items-center justify-center">
                <FileText className="w-16 h-16 text-primary-foreground" />
              </div>
            </div>
          </Card>
        )}

        {/* Stats Overview */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 border-2 hover:border-primary/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm">Total Drafts</span>
              <FileText className="w-5 h-5 text-primary" />
            </div>
            <div className="text-3xl font-bold">{stats.draftsThisWeek}</div>
            <p className="text-xs text-muted-foreground mt-1">Newsletter drafts</p>
          </Card>

          <Card className="p-6 border-2 hover:border-primary/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm">Acceptance Rate</span>
              <CheckCircle2 className="w-5 h-5 text-primary" />
            </div>
            <div className="text-3xl font-bold">{stats.acceptanceRate}%</div>
            <p className="text-xs text-muted-foreground mt-1">Above target</p>
          </Card>

          <Card className="p-6 border-2 hover:border-primary/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm">Avg Gen Time</span>
              <Clock className="w-5 h-5 text-primary" />
            </div>
            <div className="text-3xl font-bold">{stats.avgReviewTime}</div>
            <p className="text-xs text-muted-foreground mt-1">Generation time</p>
          </Card>

          <Card className="p-6 border-2 hover:border-primary/50 transition-all duration-300">
            <div className="flex items-center justify-between mb-2">
              <span className="text-muted-foreground text-sm">Engagement</span>
              <BarChart3 className="w-5 h-5 text-primary" />
            </div>
            <div className="text-3xl font-bold">{stats.engagement}</div>
            <p className="text-xs text-muted-foreground mt-1">vs baseline</p>
          </Card>
        </div>

        {/* Quick Start Guide for New Users - Only show if no sources */}
        {sourceCount === 0 && (
          <Card className="p-8 mb-8 border-2" id="how-to-start">
            <h2 className="text-2xl font-bold mb-6">🚀 Quick Start Guide</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-primary">1</span>
                </div>
                <h3 className="font-semibold mb-2">Add Sources</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Connect Twitter accounts, YouTube channels, or RSS feeds you follow
                </p>
                <Link to="/sources">
                  <Button variant="outline" size="sm">
                    Go to Sources
                  </Button>
                </Link>
              </div>

              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-primary">2</span>
                </div>
                <h3 className="font-semibold mb-2">Generate Draft</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  AI analyzes your sources and creates a personalized newsletter
                </p>
                <Link to="/drafts">
                  <Button variant="outline" size="sm">
                    Go to Drafts
                  </Button>
                </Link>
              </div>

              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-primary">3</span>
                </div>
                <h3 className="font-semibold mb-2">Review & Send</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Quick review and send to your subscribers
                </p>
                <Link to="/drafts">
                  <Button variant="outline" size="sm">
                    Go to Drafts
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        )}

        {/* Recent Drafts - Full Width */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">Recent Drafts</h2>
            <Link to="/drafts">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </div>

          <div className="space-y-4">
            {recentDrafts.length === 0 ? (
              <Card className="p-12 border-2 text-center bg-muted/30">
                <FileText className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-xl font-semibold mb-2">No Drafts Yet</h3>
                <p className="text-muted-foreground mb-6">
                  {sourceCount === 0
                    ? "Add content sources first, then generate your first AI-powered newsletter draft"
                    : "You have sources connected! Generate your first newsletter draft from them."}
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  {sourceCount === 0 ? (
                    <Link to="/sources">
                      <Button variant="hero">
                        <Plus className="w-4 h-4 mr-2" />
                        Add Sources First
                      </Button>
                    </Link>
                  ) : (
                    <Link to="/drafts">
                      <Button variant="hero">
                        <Plus className="w-4 h-4 mr-2" />
                        Generate Draft
                      </Button>
                    </Link>
                  )}
                  <Link to="/drafts">
                    <Button variant="outline">
                      View Drafts Page
                    </Button>
                  </Link>
                </div>
              </Card>
            ) : (
              recentDrafts.map((draft) => (
                <Card
                  key={draft.id}
                  className="p-6 border-2 hover:border-primary/50 transition-all duration-300 cursor-pointer group"
                  onClick={() => navigate("/drafts")}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
                          {draft.subject || "Untitled Draft"}
                        </h3>
                        <span
                          className={`text-xs px-2 py-1 rounded-full ${
                            draft.status === "pending"
                              ? "bg-primary/10 text-primary"
                              : draft.status === "sent"
                              ? "bg-muted text-muted-foreground"
                              : "bg-secondary/10 text-secondary"
                          }`}
                        >
                          {draft.status === "pending"
                            ? "Ready to Review"
                            : draft.status.charAt(0).toUpperCase() +
                              draft.status.slice(1)}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {new Date(draft.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    {draft.status === "pending" && (
                      <Button variant="hero" size="sm">
                        Review
                      </Button>
                    )}
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
