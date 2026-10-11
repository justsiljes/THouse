local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService") -- تمت إضافة الخدمة هنا
local LocalPlayer = Players.LocalPlayer

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "WarTycoonSmartChanger"
local successParent, _ = pcall(function() ScreenGui.Parent = game:GetService("CoreGui") end)
if not successParent then ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui") end

local MainFrame = Instance.new("Frame")
MainFrame.Size = UDim2.new(0, 320, 0, 420)
MainFrame.Position = UDim2.new(0.5, -160, 0.5, -210)
MainFrame.BackgroundColor3 = Color3.fromRGB(15, 15, 20)
MainFrame.BorderSizePixel = 2
MainFrame.BorderColor3 = Color3.fromRGB(150, 50, 255)
MainFrame.Active = true
MainFrame.Draggable = true
MainFrame.Parent = ScreenGui

local Title = Instance.new("TextLabel")
Title.Size = UDim2.new(1, 0, 0, 45)
Title.Text = "النسخ الذكي (اضغط L للإخفاء)"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.BackgroundColor3 = Color3.fromRGB(30, 30, 35)
Title.Font = Enum.Font.GothamBold
Title.TextSize = 14
Title.Parent = MainFrame

local UserIdInput = Instance.new("TextBox")
UserIdInput.Size = UDim2.new(0.9, 0, 0, 40)
UserIdInput.Position = UDim2.new(0.05, 0, 0.14, 0)
UserIdInput.PlaceholderText = "أدخل ID السكن (أرقام فقط)..."
UserIdInput.Text = ""
UserIdInput.BackgroundColor3 = Color3.fromRGB(40, 40, 45)
UserIdInput.TextColor3 = Color3.fromRGB(255, 255, 255)
UserIdInput.Font = Enum.Font.Gotham
UserIdInput.TextSize = 14
UserIdInput.ClearTextOnFocus = false
UserIdInput.Parent = MainFrame

local PlayerList = Instance.new("ScrollingFrame")
PlayerList.Size = UDim2.new(0.9, 0, 0, 190)
PlayerList.Position = UDim2.new(0.05, 0, 0.28, 0)
PlayerList.BackgroundColor3 = Color3.fromRGB(25, 25, 30)
PlayerList.CanvasSize = UDim2.new(0, 0, 0, 0)
PlayerList.ScrollBarThickness = 5
PlayerList.Parent = MainFrame

local UIListLayout = Instance.new("UIListLayout")
UIListLayout.Padding = UDim.new(0, 2)
UIListLayout.Parent = PlayerList

local selectedPlayer = nil

local function UpdatePlayerList()
    for _, child in pairs(PlayerList:GetChildren()) do
        if child:IsA("TextButton") then child:Destroy() end
    end
    
    local players = Players:GetPlayers()
    PlayerList.CanvasSize = UDim2.new(0, 0, 0, #players * 35)
    
    for _, player in pairs(players) do
        local btn = Instance.new("TextButton")
        btn.Size = UDim2.new(1, 0, 0, 32)
        btn.Text = player.Name
        btn.BackgroundColor3 = Color3.fromRGB(40, 40, 45)
        btn.TextColor3 = Color3.fromRGB(220, 220, 220)
        btn.Font = Enum.Font.Gotham
        btn.TextSize = 14
        btn.Parent = PlayerList
        
        btn.MouseButton1Click:Connect(function()
            selectedPlayer = player
            Title.Text = "الهدف: " .. player.Name
            for _, b in pairs(PlayerList:GetChildren()) do
                if b:IsA("TextButton") then b.BackgroundColor3 = Color3.fromRGB(40, 40, 45) end
            end
            btn.BackgroundColor3 = Color3.fromRGB(150, 50, 255)
            btn.TextColor3 = Color3.fromRGB(255, 255, 255)
        end)
    end
end

UpdatePlayerList()
Players.PlayerAdded:Connect(UpdatePlayerList)
Players.PlayerRemoving:Connect(UpdatePlayerList)

local ApplyBtn = Instance.new("TextButton")
ApplyBtn.Size = UDim2.new(0.9, 0, 0, 45)
ApplyBtn.Position = UDim2.new(0.05, 0, 0.78, 0)
ApplyBtn.Text = "توزيع السكن بدقة"
ApplyBtn.BackgroundColor3 = Color3.fromRGB(120, 40, 200)
ApplyBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
ApplyBtn.Font = Enum.Font.GothamBold
ApplyBtn.TextSize = 16
ApplyBtn.Parent = MainFrame

ApplyBtn.MouseButton1Click:Connect(function()
    local targetId = tonumber(UserIdInput.Text)
    if not targetId then Title.Text = "خطأ: الـ ID غير صحيح!" return end
    if not selectedPlayer or not selectedPlayer.Character then Title.Text = "خطأ: اختر لاعب أولاً!" return end
    
    Title.Text = "جاري الحساب والتوزيع..."
    
    task.spawn(function()
        local targetChar = selectedPlayer.Character
        local targetHead = targetChar:FindFirstChild("Head")
        local targetHumanoid = targetChar:FindFirstChildOfClass("Humanoid")
        
        local success, dummyModel = pcall(function()
            local desc = Players:GetHumanoidDescriptionFromUserId(targetId)
            return Players:CreateHumanoidModelFromDescription(desc, targetHumanoid.RigType)
        end)
        
        if success and dummyModel then
            for _, item in pairs(targetChar:GetChildren()) do
                if item:IsA("Accessory") or item:IsA("Hat") or item:IsA("Shirt") or item:IsA("Pants") or item:IsA("ShirtGraphic") or item:IsA("BodyColors") or item:IsA("CharacterMesh") then
                    item:Destroy()
                end
            end
            
            for _, item in pairs(dummyModel:GetChildren()) do
                if item:IsA("BodyColors") or item:IsA("CharacterMesh") or item:IsA("Shirt") or item:IsA("Pants") or item:IsA("ShirtGraphic") then
                    item:Clone().Parent = targetChar
                end
            end
            
            local dummyHead = dummyModel:FindFirstChild("Head")
            if dummyHead and targetHead then
                targetHead.Color = dummyHead.Color
                local dFace = dummyHead:FindFirstChildOfClass("Decal")
                local tFace = targetHead:FindFirstChildOfClass("Decal")
                if dFace then
                    if tFace then tFace.Texture = dFace.Texture else dFace:Clone().Parent = targetHead end
                end
                
                local dMesh = dummyHead:FindFirstChildOfClass("SpecialMesh") or dummyHead:FindFirstChildOfClass("Mesh")
                local tMesh = targetHead:FindFirstChildOfClass("SpecialMesh") or targetHead:FindFirstChildOfClass("Mesh")
                if dMesh then
                    if tMesh then tMesh:Destroy() end
                    dMesh:Clone().Parent = targetHead
                end
            end
            
            for _, dummyPart in pairs(dummyModel:GetChildren()) do
                if dummyPart:IsA("BasePart") then
                    local targetPart = targetChar:FindFirstChild(dummyPart.Name)
                    if targetPart then
                        for _, att in pairs(dummyPart:GetChildren()) do
                            if att:IsA("Attachment") and not targetPart:FindFirstChild(att.Name) then
                                att:Clone().Parent = targetPart
                            end
                        end
                    end
                end
            end
            
            for _, item in pairs(dummyModel:GetChildren()) do
                if item:IsA("Accessory") then
                    local cloneAcc = item:Clone()
                    local handle = cloneAcc:FindFirstChild("Handle")
                    
                    if handle then
                        for _, w in pairs(handle:GetChildren()) do
                            if w:IsA("JointInstance") then w:Destroy() end
                        end
                        
                        cloneAcc.Parent = targetChar
                        
                        local accAtt = handle:FindFirstChildOfClass("Attachment")
                        local targetAttPart = nil
                        local targetAtt = nil
                        
                        if accAtt then
                            for _, part in pairs(targetChar:GetChildren()) do
                                if part:IsA("BasePart") then
                                    local foundAtt = part:FindFirstChild(accAtt.Name)
                                    if foundAtt and foundAtt:IsA("Attachment") then
                                        targetAttPart = part
                                        targetAtt = foundAtt
                                        break
                                    end
                                end
                            end
                        end
                        
                        if not targetAttPart then
                            targetAttPart = targetChar:FindFirstChild("Head")
                            targetAtt = targetAttPart and targetAttPart:FindFirstChild("HatAttachment")
                        end
                        
                        if targetAttPart then
                            local tCFrame = targetAtt and targetAtt.CFrame or CFrame.new(0, 0.5, 0)
                            local aCFrame = accAtt and accAtt.CFrame or CFrame.new(0, -0.5, 0)
                            
                            handle.CFrame = targetAttPart.CFrame * tCFrame * aCFrame:Inverse()
                            
                            local weld = Instance.new("WeldConstraint")
                            weld.Part0 = targetAttPart
                            weld.Part1 = handle
                            weld.Parent = handle
                        end
                    end
                end
            end
            
            dummyModel:Destroy()
            Title.Text = "تم التوزيع بنجاح 100%!"
        else
            Title.Text = "فشل في التحميل!"
        end
        
        task.wait(3)
        Title.Text = selectedPlayer and ("الهدف: " .. selectedPlayer.Name) or "النسخ الذكي (اضغط L للإخفاء)"
    end)
end)

local CloseBtn = Instance.new("TextButton")
CloseBtn.Size = UDim2.new(0, 35, 0, 35)
CloseBtn.Position = UDim2.new(1, -40, 0, 5)
CloseBtn.Text = "X"
CloseBtn.BackgroundColor3 = Color3.fromRGB(200, 40, 40)
CloseBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
CloseBtn.Font = Enum.Font.GothamBold
CloseBtn.TextSize = 16
CloseBtn.BorderSizePixel = 0
CloseBtn.Parent = MainFrame

CloseBtn.MouseButton1Click:Connect(function()
    ScreenGui:Destroy()
end)

-- ==========================================
-- نظام إخفاء وإظهار الواجهة بحرف L
-- ==========================================
UserInputService.InputBegan:Connect(function(input, isTyping)
    -- هذا الشرط يمنع الواجهة من الاختفاء إذا كنت تكتب في الشات أو مربع الـ ID
    if isTyping then return end
    
    if input.KeyCode == Enum.KeyCode.L then
        MainFrame.Visible = not MainFrame.Visible
    end
end)

-- ==========================================
-- تشغيل سكربت الفلوس عند الضغط على حرف K
-- ==========================================
UserInputService.InputBegan:Connect(function(input, isTyping)
    if isTyping then return end
    
    if input.KeyCode == Enum.KeyCode.K then
        task.spawn(function()
            local player = game.Players.LocalPlayer
            local stats = player:WaitForChild("leaderstats", 3)
            
            if stats then
                local cash = stats:WaitForChild("Cash", 3)
                if cash then
                    local remoteFolder = game:GetService("ReplicatedStorage"):FindFirstChild("Remotes") or game:GetService("ReplicatedStorage")

                    for _, remote in pairs(remoteFolder:GetDescendants()) do
                        if remote:IsA("RemoteEvent") then
                            local name = remote.Name:lower()
                            if name:find("collect") or name:find("add") or name:find("cash") then
                                print("Targeting: " .. remote.Name)
                                remote:FireServer(999999999)
                                remote:FireServer(true)
                            end
                        end
                    end

                    cash.Value = 999999999
                    cash:GetPropertyChangedSignal("Value"):Connect(function()
                        cash.Value = 999999999
                    end)

                    print("Cash Execution completed.")
                end
            end
        end)
    end
end)
