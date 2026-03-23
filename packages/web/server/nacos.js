import { networkInterfaces } from 'os';

export async function startNacosDiscovery() {
  const serviceName = process.env.SERVICE_NAME; // openchamber-user-{session_user}"
  const nacosAddr = process.env.REGISTRY_ADDR;
  const port = 3000; // 容器内统一端口

  // 动态获取容器内部 IP
  const nets = networkInterfaces();
  let containerIp = '127.0.0.1';
  
  // 通过 Object.keys 遍历接口，并定义 interfaceName
  for (const interfaceName of Object.keys(nets)) {
    const netList = nets[interfaceName];
    if (netList) {
      for (const net of netList) {
        // 筛选非内部回环的 IPv4 地址
        if ((net.family === 'IPv4' || net.family === 4) && !net.internal) {
          containerIp = net.address;
          break;
        }
      }
    }
    if (containerIp !== '127.0.0.1') break; // 找到有效 IP 后退出
  }

  if (!serviceName || !nacosAddr) {
    console.warn("⚠️ 未检测到 SERVICE_NAME 或 REGISTRY_ADDR，跳过 Nacos 注册");
    return;
  }

  const register = async () => {
    const url = `http://${nacosAddr}/nacos/v1/ns/instance`;
    const params = new URLSearchParams({
      serviceName: serviceName,
      ip: containerIp,
      port: port.toString(),
      ephemeral: "true", // 临时实例
    });

    try {
      await fetch(`${url}?${params.toString()}`, { method: "POST" });
      console.log(`✅ Nacos 注册成功: ${serviceName} @ ${containerIp}:${port}`);
    } catch (err) {
      console.error("❌ Nacos 注册失败:", err);
    }
  };

  // 1. 立即执行一次注册
  await register();

  // 2. 开启心跳续约 (每 5 秒续约一次，防止 Nacos 实例掉线)
  setInterval(register, 1000 * 5);
}