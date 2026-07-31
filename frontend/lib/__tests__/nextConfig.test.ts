import nextConfig from "../../next.config";

describe("Next development origin policy", () => {
  it("allows the documented loopback URL used by the local review workspace", () => {
    expect(nextConfig.allowedDevOrigins).toContain("127.0.0.1");
  });
});
